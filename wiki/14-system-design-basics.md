---
title: "시스템 설계 기초 — 캐싱 · DB 스케일링 · 통신 · 로드 밸런싱"
tags: [architecture-patterns, sdlc, agent-design]
source: "raw/01_system_design_basics/"
date: 2026-06-13
related: ["[[11-architecture-decision-guide]]", "[[12-architecture-patterns]]", "[[13-microservices-patterns]]"]
version: 1
---

# 시스템 설계 기초

> 캐싱, DB 스케일링, 동기/비동기 통신, 로드 밸런싱의 핵심 개념과 개인 프로젝트에서의 적용 기준을 정리한다.

---

## Overview

어떤 아키텍처 패턴을 선택하든, 시스템 설계에서 반복적으로 등장하는 기초 개념들이 있다. 이 페이지는 그 중 가장 중요한 4가지 — 캐싱, DB 스케일링, 통신 방식, 로드 밸런싱 — 을 에이전트가 설계 결정 시 참조할 수 있도록 정리한 레퍼런스다.

---

## Key Concepts

### 1. 캐싱 전략

캐싱은 자주 사용되는 데이터를 더 빠른 저장소(메모리)에 임시 보관하여 응답 속도를 높이고 DB 부하를 줄이는 기법.

| 패턴 | 동작 | 장점 | 단점 |
|---|---|---|---|
| **Cache-Aside** (Lazy Loading) | 캐시 조회 → Miss 시 DB에서 읽어 캐시 저장 | 필요한 데이터만 적재, 구현 단순 | 첫 요청은 항상 느림, 불일치 가능 |
| **Write-Through** | 쓸 때 캐시·DB에 동시 기록 | 항상 최신 동기화 | 쓰기 지연 증가 |
| **Write-Back** (Write-Behind) | 캐시에 먼저 쓰고 주기적으로 DB 반영 | 쓰기 성능 최대화 | 캐시 장애 시 데이터 손실 위험 |

**캐시 무효화 전략**:
- TTL(Time-To-Live): 일정 시간 후 자동 만료
- Event-Based: 데이터 변경 이벤트 발생 시 캐시 삭제
- Write-Through: 쓰기 시 캐시도 동시 갱신

**개인 프로젝트 권장**: Cache-Aside + TTL (구현 단순, Redis 사용)

### 2. 데이터베이스 스케일링

**수직 확장 (Scale Up)**
```
단일 서버 사양 업그레이드 (CPU, 메모리, 디스크)
장점: 구조 변경 없이 적용, 단순함
단점: 물리적 한계, 단일 장애점(SPOF)
```

**수평 확장 (Scale Out)**

| 방법 | 구조 | 장점 | 단점 |
|---|---|---|---|
| **리플리케이션** | Master(쓰기) + Replica(읽기) 분리 | 읽기 성능 향상, 페일오버 가능 | 복제 지연 → 일시적 불일치 |
| **샤딩** | 데이터를 여러 서버에 분할 저장 | 쓰기/읽기 모두 수평 확장 | 샤드 간 JOIN 어려움, 리샤딩 비용, 운영 복잡 |

**개인 프로젝트 권장 순서**:
```
1. 단일 DB로 시작
2. 읽기 부하 증가 → Read Replica 추가
3. 쓰기 부하 증가 → 수직 확장 or 샤딩 (샤딩은 최후 수단)
```

### 3. 동기 vs 비동기 통신

| 구분 | 예시 | 장점 | 단점 |
|---|---|---|---|
| **동기** | REST API, gRPC | 흐름 직관적, 디버깅 용이, 즉시 결과 확인 | 대상 서비스 느리면 호출자도 영향 받음 (강한 결합) |
| **비동기** | 메시지 큐, Pub/Sub | 느슨한 결합, 트래픽 버퍼링, 장애 격리 | 흐름 추적 어려움, 즉시 응답 불가 |

**선택 기준**:

| 상황 | 권장 |
|---|---|
| 사용자가 결과를 즉시 확인해야 함 (로그인, 조회) | 동기 |
| 즉시 응답 불필요한 후속 작업 (이메일 발송, 썸네일 생성, 알림) | 비동기 |
| 여러 서비스에 동일 이벤트를 전파해야 함 | 비동기 (Pub/Sub) |

### 4. 로드 밸런싱

하나의 서버로 처리하기 어려운 트래픽을 여러 서버 인스턴스에 분산.

**주요 알고리즘**:

| 알고리즘 | 동작 | 적합한 상황 |
|---|---|---|
| Round Robin | 순서대로 균등 분배 | 서버 성능이 비슷할 때 |
| Least Connections | 현재 연결 수 가장 적은 서버로 | 요청 처리 시간이 불균일할 때 |
| IP Hash / Consistent Hashing | 특정 클라이언트 → 항상 같은 서버 | 세션 유지 필요할 때 |

**적용 위치**:
```
클라이언트 → [L7 로드밸런서] → 서버 인스턴스 A/B/C
                                         ↓
                             [DB 로드밸런서] → Read Replica A/B
```

> **개인 프로젝트**: 초기에는 불필요. 클라우드 PaaS의 기본 로드밸런싱(헬스체크, 무중단 배포)은 활용 권장.

---

## Details

### 캐싱 적용 포인트 결정

```
에이전트가 캐싱 도입 시 반드시 답해야 할 질문:

1. 어떤 데이터를 캐싱할 것인가?
   → 읽기 多, 쓰기 少, 계산 비용 높은 데이터

2. 캐시 키(Key) 설계는?
   → user:{id}:profile, product:{id}:detail

3. TTL은 얼마나?
   → 데이터 변경 빈도와 허용 가능한 staleness에 따라

4. 무효화(invalidation) 시점은?
   → 데이터 업데이트 이벤트 발생 시

5. 캐시 Miss 시 어떻게 처리?
   → DB에서 읽어와 캐시에 저장 (Cache-Aside)
```

### 개인 프로젝트 시스템 설계 기본 스택 (권장)

```
트래픽 분산: 클라우드 PaaS 기본 LB (nginx 또는 클라우드 제공)
캐싱: Redis (Cache-Aside + TTL)
DB: PostgreSQL (단일 인스턴스로 시작)
비동기 처리: Redis Pub/Sub 또는 단순 Background Worker (Celery 등)
외부 API 보호: Circuit Breaker (Resilience4j, Hystrix 등)
```

---

## Examples / Code

### Cache-Aside 구현 (Python + Redis)

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379)
TTL = 300  # 5분

def get_user(user_id: int) -> dict:
    key = f"user:{user_id}:profile"
    
    # 캐시 조회
    cached = cache.get(key)
    if cached:
        return json.loads(cached)  # Cache Hit
    
    # Cache Miss → DB 조회
    user = db.query(User).filter(User.id == user_id).first()
    result = user.to_dict()
    
    # 캐시에 저장 (TTL 설정)
    cache.setex(key, TTL, json.dumps(result))
    return result

def update_user(user_id: int, data: dict):
    db.query(User).filter(User.id == user_id).update(data)
    db.commit()
    
    # 캐시 무효화
    cache.delete(f"user:{user_id}:profile")
```

---

## Related

- [[11-architecture-decision-guide]] — 읽기/쓰기 비율 기반 캐싱·DB 스케일링 결정
- [[12-architecture-patterns]] — 전체 아키텍처 패턴 선택
- [[13-microservices-patterns]] — Circuit Breaker, API Gateway 등 분산 시스템 패턴
