# 레이어드 아키텍처 / 모듈형 모놀리식

## 레이어드 아키텍처 (Layered Architecture)
계층별로 책임을 분리하는 가장 기본적인 구조.

- Presentation Layer: 사용자 입출력 처리 (API 엔드포인트, UI)
- Business/Application Layer: 핵심 로직, 도메인 규칙
- Data Access Layer: DB/외부 저장소와의 통신
- (선택) Infrastructure Layer: 외부 서비스 연동, 메시징 등

장점: 구조가 단순하고 이해하기 쉬움, 작은 프로젝트에 적합
단점: 계층 간 의존이 과도해지면 변경 시 여러 계층을 동시에 수정해야 함

## 모듈형 모놀리식 (Modular Monolith)
하나의 배포 단위(모놀리식) 안에서, 기능 영역별로 모듈(도메인)을 명확히 분리하는 구조.

- 예: `user/`, `order/`, `payment/`, `notification/` 모듈이 각각 자신의
  레이어드 구조(controller-service-repository)를 가지되, 모듈 간 통신은
  명확히 정의된 인터페이스를 통해서만 이루어짐
- 모듈 간 직접 DB 테이블 참조를 금지하고, 서비스 레이어를 통해서만 접근

장점:
- 단일 배포/단일 DB로 운영이 단순함 (개인 프로젝트에 적합)
- 모듈 경계가 명확해 추후 마이크로서비스로 분리하기 쉬움
- 트랜잭션 관리가 단순함 (DB 트랜잭션 그대로 활용 가능)

단점:
- 모듈 경계 규칙을 지키지 않으면 시간이 지나며 Big Ball of Mud(06_antipatterns 참고)로 변질될 위험

## 권장 사용 시점
- 1인 개발, MVP, 초기 프로젝트 전반에 기본값으로 권장
- "특정 모듈만 트래픽이 폭증한다"는 명확한 신호가 있을 때, 그 모듈만 분리해서
  마이크로서비스(02_microservices_architecture.md)로 전환하는 점진적 접근이 안전함
