---
title: "아키텍처 패턴 — Layered · Microservices · Event-Driven · CQRS"
tags: [architecture-patterns, agent-design, sdlc]
source: "raw/02_architecture_patterns/"
date: 2026-06-13
related: ["[[11-architecture-decision-guide]]", "[[13-microservices-patterns]]", "[[16-architecture-antipatterns]]"]
version: 1
---

# 아키텍처 패턴 — Layered · Microservices · Event-Driven · CQRS

> 개인 프로젝트에서 선택 가능한 주요 아키텍처 스타일 4종. 각 패턴의 구조·장단점·도입 시점을 비교한다.

---

## Overview

아키텍처 패턴은 시스템의 구성 요소를 어떻게 분리하고 연결할지를 결정하는 큰 틀이다. 잘못된 패턴 선택은 운영 복잡도·기술 부채의 원인이 되므로, [[10-project-classification]] → [[11-architecture-decision-guide]] 순서로 프로젝트 특성을 먼저 파악한 뒤 이 페이지의 패턴 중 하나를 선택한다.

---

## Key Concepts

### 1. 레이어드 아키텍처 (Layered Architecture)

계층별로 책임을 분리하는 가장 기본적인 구조.

```
┌────────────────────────────────┐
│   Presentation Layer           │  ← API 엔드포인트, UI
├────────────────────────────────┤
│   Business / Application Layer │  ← 핵심 로직, 도메인 규칙
├────────────────────────────────┤
│   Data Access Layer            │  ← DB / 외부 저장소 통신
├────────────────────────────────┤
│   Infrastructure Layer (선택)  │  ← 외부 서비스 연동, 메시징
└────────────────────────────────┘
```

| | |
|---|---|
| **장점** | 구조가 단순하고 이해하기 쉬움, 소규모 프로젝트에 적합 |
| **단점** | 계층 간 의존이 과도해지면 변경 시 여러 계층을 동시에 수정해야 함 |

### 2. 모듈형 모놀리식 (Modular Monolith)

하나의 배포 단위(모놀리식) 안에서, 기능 영역별로 모듈(도메인)을 명확히 분리하는 구조.

```
[ 단일 배포 단위 ]
├── user/      (controller - service - repository)
├── order/     (controller - service - repository)
├── payment/   (controller - service - repository)
└── notification/ ...
    ↑ 모듈 간 통신은 서비스 레이어 인터페이스로만
    ↑ 모듈 간 직접 DB 테이블 참조 금지
```

| | |
|---|---|
| **장점** | 단일 배포/단일 DB, 트랜잭션 단순, 추후 마이크로서비스 분리 용이 |
| **단점** | 경계 규칙을 지키지 않으면 Big Ball of Mud([[16-architecture-antipatterns]])로 변질 |
| **권장 사용 시점** | **개인 프로젝트·MVP·초기 단계의 기본값** |

### 3. 마이크로서비스 (Microservices)

비즈니스 기능 단위의 작은 서비스들로 분리. 각 서비스가 독립적으로 배포·확장·개발된다.

```
Client → API Gateway
              ├── User Service    (DB: PostgreSQL)
              ├── Order Service   (DB: MongoDB)
              ├── Payment Service (DB: MySQL)
              └── Notification    (Queue: RabbitMQ)
```

| | |
|---|---|
| **장점** | 서비스별 독립 배포·확장, Polyglot 기술 스택, 장애 격리 |
| **단점** | 서비스 간 통신 지연, 분산 트랜잭션 복잡(→ Saga), 운영 복잡도 급증 |
| **도입 판단** | 팀이 서비스별로 독립 작업 필요하거나, 특정 기능의 부하가 크게 다를 때만 |

> **함정**: 개인 프로젝트에서 처음부터 마이크로서비스를 도입하는 것은 **Golden Hammer** 안티패턴이다.

### 4. 이벤트 드리븐 아키텍처 (Event-Driven)

컴포넌트들이 이벤트를 발행(publish)하고 구독(subscribe)하여 반응하는 구조.

```
Producer → [Event Broker: Kafka/RabbitMQ] → Consumer A
                                           → Consumer B
                                           → Consumer C
```

| 구성 요소 | 역할 |
|---|---|
| Producer | 상태 변화가 발생한 쪽 ("주문이 생성됨") |
| Event Broker | 이벤트 전달 매개체 (Kafka, RabbitMQ, SNS/SQS) |
| Consumer | 이벤트에 반응하여 후속 작업 수행 (알림, 재고 차감) |

| | |
|---|---|
| **장점** | 컴포넌트 간 느슨한 결합, 새 기능 추가 시 기존 코드 수정 불필요, 트래픽 버퍼링 |
| **단점** | 전체 데이터 흐름 파악 어려움, 이벤트 순서·중복 처리 고려 필요 |
| **개인 프로젝트 적용** | 모든 통신을 이벤트로 만들지 말 것. 즉시 응답 불필요한 후속 처리(알림, 통계)에만 적용 |

### 5. CQRS와 이벤트 소싱

**CQRS (Command Query Responsibility Segregation)**

```
Command (쓰기 모델)   → 비즈니스 규칙 검증, 트랜잭션 처리
Query  (조회 모델)    → 화면에 최적화된 형태로 데이터 제공
         ↑ 같은 DB 또는 완전히 분리된 저장소 사용 가능
```

**이벤트 소싱 (Event Sourcing)**

```
현재 상태 직접 저장(×) → "잔액 = 1000원"
이벤트 목록 저장(○) → "입금 1000원", "출금 200원" → replay → 1000원
```

| | |
|---|---|
| **CQRS 단점** | 두 모델 간 동기화 지연(결과적 일관성), 단순 CRUD 대비 복잡도 급증 |
| **적용 기준** | 읽기 패턴이 매우 복잡하거나 읽기/쓰기 부하 특성이 크게 다를 때만 |

---

## Details

### 패턴 선택 매트릭스

| 조건 | 추천 패턴 |
|---|---|
| 1인 개발, MVP | **모듈형 모놀리식** |
| 읽기 부하 집중 | 모듈형 모놀리식 + **Redis 캐시** |
| 특정 모듈만 부하 큼 | 해당 모듈만 **마이크로서비스로 분리** |
| 비동기 후속 처리 많음 | **이벤트 드리븐** (부분 적용) |
| 조회 모델 복잡 | **CQRS** (부분 적용) |

### 점진적 진화 전략 (권장)

```
1단계: 모듈형 모놀리식으로 시작
         ↓ 특정 모듈 트래픽 폭증 감지
2단계: 해당 모듈만 서비스로 분리 (Strangler Fig 패턴)
         ↓ 비동기 처리 필요 증가
3단계: 이벤트 드리븐 요소 부분 도입
         ↓ 조회 최적화 필요
4단계: CQRS 조회 모델 추가
```

---

## Examples / Code

### 모듈형 모놀리식 패키지 구조 예시 (Spring Boot)

```
src/main/java/com/example/
├── user/
│   ├── UserController.java
│   ├── UserService.java
│   └── UserRepository.java
├── order/
│   ├── OrderController.java
│   ├── OrderService.java   ← UserService 주입 (인터페이스로)
│   └── OrderRepository.java
└── common/
    ├── auth/
    └── exception/
```

---

## Related

- [[10-project-classification]] — 패턴 선택 전 프로젝트 특성 파악
- [[11-architecture-decision-guide]] — 특성 기반 패턴 선택 매핑 가이드
- [[13-microservices-patterns]] — 마이크로서비스 도입 시 필요한 보조 패턴
- [[16-architecture-antipatterns]] — 잘못된 패턴 선택의 결과
