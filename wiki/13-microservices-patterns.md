---
title: "마이크로서비스 보조 패턴 — Saga · API Gateway · Circuit Breaker 외"
tags: [architecture-patterns, agent-design, sdlc]
source: "raw/03_microservices_patterns/"
date: 2026-06-13
related: ["[[12-architecture-patterns]]", "[[14-system-design-basics]]", "[[11-architecture-decision-guide]]"]
version: 1
---

# 마이크로서비스 보조 패턴

> 마이크로서비스 아키텍처([[12-architecture-patterns]])를 도입했을 때 발생하는 문제들을 해결하기 위한 6가지 보조 패턴. 개인 프로젝트에서의 적용 기준도 함께 정리한다.

---

## Overview

마이크로서비스를 도입하면 "서비스 간 데이터 통합", "분산 트랜잭션", "외부 장애 전파" 같은 새로운 문제가 생긴다. 이 페이지의 패턴들은 그 문제를 해결하기 위한 것이다. 단, 개인 프로젝트·모듈형 모놀리식 단계에서는 대부분 불필요하다.

---

## Key Concepts

### 1. Database per Service

**문제**: 여러 서비스가 하나의 DB를 공유하면 서비스 간 결합도가 높아져 독립 배포가 어려워진다.

**해결**: 각 서비스는 자신만의 데이터 저장소를 가지며, 다른 서비스는 반드시 해당 서비스의 API를 통해서만 접근한다.

```
User Service    → PostgreSQL
Order Service   → MongoDB
Analytics       → ClickHouse
(X) Order Service가 User DB에 직접 접근
(O) Order Service → User Service API → User DB
```

| | |
|---|---|
| **장점** | 서비스 간 결합도 감소, 서비스별 최적 DB 선택, 독립 배포 용이 |
| **단점** | 여러 서비스 데이터 Join 불가 → API Composition 또는 CQRS 필요 |
| **개인 프로젝트** | 모듈형 모놀리식 단계: "하나의 DB, 모듈별 스키마 분리"로 시작 |

### 2. Saga 패턴 (분산 트랜잭션)

**문제**: 서비스마다 별도 DB를 가지면 여러 서비스에 걸친 작업을 하나의 DB 트랜잭션으로 묶을 수 없다.

**해결**: 비즈니스 트랜잭션을 로컬 트랜잭션의 순서로 나누고, 실패 시 보상 트랜잭션(Compensating Transaction)을 실행한다.

```
주문 생성 → [주문 서비스: 주문 저장]
              → 이벤트 발행: "주문 생성됨"
                → [결제 서비스: 결제 처리]
                    → 이벤트: "결제 완료"
                      → [재고 서비스: 재고 차감]

실패 시: 역순으로 보상 트랜잭션 실행
```

**두 가지 구현 방식**:

| 방식 | 설명 | 적합한 경우 |
|---|---|---|
| Choreography | 각 서비스가 이벤트를 구독하고 자율적으로 다음 행동 결정 (중앙 제어자 없음) | 단순한 흐름 |
| Orchestration | 별도의 오케스트레이터가 각 단계 호출, 실패 시 보상 지시 | 복잡한 흐름, 가시성 중요 |

### 3. API Gateway 패턴

**문제**: 클라이언트가 여러 서비스에 직접 요청 → 서비스 주소를 모두 알아야 하고, 공통 로직(인증, 로깅)을 모든 서비스가 각자 구현해야 한다.

**해결**: 단일 진입점(API Gateway)이 모든 요청을 받아 적절한 내부 서비스로 라우팅하고, 공통 로직을 중앙에서 처리한다.

```
Client → [API Gateway]
              ├── /users/**    → User Service
              ├── /orders/**   → Order Service
              └── /payments/** → Payment Service
          ↑ 인증, 로깅, Rate Limiting, SSL Termination
```

| | |
|---|---|
| **장점** | 클라이언트 통합 단순화, 공통 로직 중앙 관리 |
| **단점** | 게이트웨이 자체가 단일 장애점(SPOF) → 이중화 필요 |
| **개인 프로젝트** | 모듈형 모놀리식 단계: 앱 자체의 공통 미들웨어(필터, 인터셉터)가 이 역할 |

### 4. API Composition 패턴

**문제**: 데이터가 여러 서비스/DB에 분산되면 단일 DB JOIN으로 조합 조회를 할 수 없다.

**해결**: API Composer가 관련 서비스에 개별 요청을 보내고, 응답을 메모리상에서 조합하여 반환한다.

```
Client → [API Composer / Gateway]
              ├── → User Service    (사용자 정보)
              ├── → Order Service   (주문 목록)
              └── → Product Service (상품 정보)
              ↓ 메모리에서 Join 후 단일 응답 반환
```

| | |
|---|---|
| **단점** | 여러 서비스 호출 → 지연 증가 (병렬 호출 + 타임아웃으로 완화) |
| **적용 기준** | 조합 데이터 양이 적고 호출 서비스 수가 많지 않을 때 |

### 5. Circuit Breaker 패턴

**문제**: 의존하는 외부 서비스가 느리거나 응답하지 않을 때, 계속 대기하면 자원(스레드, 커넥션)이 고갈되어 호출하는 서비스도 다운된다 (장애 전파).

**해결**: 실패율이 임계값을 넘으면 회로를 차단(Open)하여 이후 요청을 즉시 Fallback 처리한다.

```
Closed → (실패율 임계값 초과) → Open → (일정 시간 후) → Half-Open
                                                          ↓ 일부 요청 통과
                                                 (정상이면) → Closed
                                                 (실패이면) → Open
```

| 상태 | 동작 |
|---|---|
| Closed | 정상 상태, 요청 그대로 전달 |
| Open | 장애 감지, 요청을 즉시 Fallback 처리 |
| Half-Open | 일부 요청만 통과시켜 복구 여부 확인 |

> **개인 프로젝트에서도 적용 가치 높음**: 외부 결제/알림 API 연동 시 적용하면 안정성 크게 향상

### 6. Sidecar 패턴

**문제**: 로깅, 모니터링, 인증 같은 공통 기능을 모든 서비스가 각자 구현 → 중복·불일치.

**해결**: 메인 앱 컨테이너 옆에 공통 기능을 담당하는 보조 프로세스(Sidecar)를 같은 Pod에 배치.

```
[ Pod ]
├── Main App Container   (비즈니스 로직)
└── Sidecar Container    (로깅, 모니터링, 통신 추상화)
```

> **개인 프로젝트**: Kubernetes를 사용하지 않는다면 직접 도입 불필요. 대신 로깅/모니터링 라이브러리를 공통 모듈로 분리하는 것으로 충분.

---

## Details

### 패턴 적용 결정표

| 문제 상황 | 적용 패턴 |
|---|---|
| 서비스 간 DB 공유로 결합도 높음 | Database per Service |
| 여러 서비스에 걸친 트랜잭션 필요 | Saga |
| 클라이언트가 서비스 주소를 여러 개 알아야 함 | API Gateway |
| 여러 서비스 데이터를 조합 조회 필요 | API Composition |
| 외부 서비스 장애가 내부로 전파됨 | Circuit Breaker |
| 공통 기능(로깅·모니터링)을 서비스마다 중복 구현 | Sidecar |

---

## Related

- [[12-architecture-patterns]] — 마이크로서비스 도입 판단 기준
- [[14-system-design-basics]] — 캐싱, DB 스케일링, 동기/비동기 통신
- [[16-architecture-antipatterns]] — 마이크로서비스를 잘못 도입했을 때의 결과
