# AI TravelTailor 설계 평가 보고서

**작성일**: 2025-10-20  
**작성자**: Codex Design Review  
**대상**: 프로젝트 문서 (`specs/001-ai-travel-planner/`, `docs/architecture-analysis-report.md`)

---

## 1. 개요

AI TravelTailor 프로젝트의 현행 설계 문서를 기반으로 아키텍처 적합성, 요구사항 정합성, 잠재적 위험 요소를 검토하였다. 본 보고서는 핵심 평가 결과와 개선 권장사항을 제공하여 향후 설계 고도화와 구현 단계 리스크를 줄이는 것을 목표로 한다.

---

## 2. 긍정적 관찰

- **요구사항 명확성**: 사용자 스토리 및 20개의 기능 요구사항이 테스트 가능한 형태로 정의되어 있어 범위가 명확하다 (`specs/001-ai-travel-planner/spec.md:10`, `specs/001-ai-travel-planner/spec.md:132`).
- **구현 계획의 단계화**: Phase별 게이트와 기술 맥락이 명확히 제시되어 팀 단위 정렬과 병렬 작업 계획 수립이 용이하다 (`specs/001-ai-travel-planner/plan.md:19`, `specs/001-ai-travel-planner/plan.md:25`).
- **사전 아키텍처 점검**: 보안·성능 항목을 선제적으로 다룬 아키텍처 분석 보고서가 존재하여 품질 확보에 기여한다 (`docs/architecture-analysis-report.md:132`, `docs/architecture-analysis-report.md:338`).

---

## 3. 주요 리스크 및 개선 필요 영역

- **인증/세션 이중화 위험**  
  Supabase Auth와 FastAPI 사용자 모델을 모두 활용하려는 설계가 토큰/세션 동기화 실패를 유발할 수 있으나 통합 전략이 정의되어 있지 않다 (`specs/001-ai-travel-planner/plan.md:39`, `specs/001-ai-travel-planner/tasks.md:42`, `docs/architecture-analysis-report.md:340`).

- **마이그레이션 체크포인트 누락**  
  기반 인프라 단계에서 Alembic 마이그레이션 스크립트(T013)가 미완료 상태로 표시되어 있어 이후 단계가 차단될 가능성이 높다 (`specs/001-ai-travel-planner/tasks.md:46`, `docs/architecture-analysis-report.md:13`).

- **장시간 작업 처리 전략 부재**  
  여행 일정 생성 API가 비동기 처리와 SLA(30초)를 요구하지만 워커/큐 등 백그라운드 처리 전략이 문서화되지 않았다 (`specs/001-ai-travel-planner/tasks.md:122`, `specs/001-ai-travel-planner/plan.md:58`).

- **프론트엔드 런타임 안정성 리스크**  
  Next.js 14, React 19와 같은 RC 수준 프레임워크를 MVP부터 채택하면 예상치 못한 Breaking Change에 노출될 수 있다 (`specs/001-ai-travel-planner/plan.md:18`).

- **PDF 생성 파이프라인 불명확**  
  Puppeteer 기반 PDF 생성을 선택했지만 Python 백엔드와의 통합 방식, 배포 환경 요구사항이 정의되지 않았다 (`specs/001-ai-travel-planner/plan.md:20`).

---

## 4. 개선 로드맵 및 실행 세부사항

### 4.1 인증 흐름 단일화

- **목적**: 단일 인증 권위를 확립해 토큰/세션 불일치 위험을 제거하고 웹·모바일 채널에서 일관된 로그인 경험을 제공한다.
- **실행 워크플로**
  1. 설계 워크숍에서 `Supabase Auth 중심`과 `FastAPI 자체 인증` 중 하나를 결정하고 근거를 기록한다.
  2. 선택안에 맞춰 토큰 발급·검증 흐름, 저장 위치(localStorage/쿠키/Native Secure Storage)를 시퀀스 다이어그램으로 문서화한다.
  3. 로그인/로그아웃, 토큰 갱신, 권한 회수 시나리오를 통합 테스트로 정의하고 QA/보안팀 리뷰를 거친다.
  4. 클라이언트 SDK(웹, Capacitor) 지침을 업데이트하고 개발자 온보딩 가이드를 개정한다.
  5. 운영 단계에서 토큰 만료, 비정상 세션 탐지 모니터링을 설정한다.
- **기술 비교**

| 항목 | Supabase Auth 중심 | FastAPI 자체 JWT |
| --- | --- | --- |
| 강점 | 이메일/소셜 로그인, 세션 관리가 기본 제공 | 백엔드에서 규칙 제어 용이, 외부 서비스 의존 감소 |
| 약점 | 서버 사이드 검증에 Supabase SDK 의존 | OAuth, 비밀번호 재설정 로직을 직접 구축해야 함 |
| 모바일 연동 | Supabase JS/Capacitor 플러그인 사용 가능 | Native Secure Storage와 토큰 갱신 로직을 자체 구현 |
| 운영 부담 | 상대적으로 낮음 (Supabase 콘솔 활용) | 자체 모니터링·로그인 관리 필요 |
| 권장 판단 | MVP 기간 신속성 중시 시 적합 | 장기적으로 커스텀 정책 필요 시 고려 |

- **산출물 & 오너**
  - 인증 아키텍처 결정 기록 (Architecture Owner)
  - 업데이트된 시퀀스 다이어그램 및 개발자 가이드 (Tech Lead)
  - 통합 테스트 스위트 및 모니터링 대시보드 (QA/DevOps)

### 4.2 Phase 2 완료 조건 재정의

- **목적**: 데이터베이스 스키마 일관성을 확보해 이후 단계 작업의 리스크를 제거한다.
- **실행 워크플로**
  1. Alembic 마이그레이션(T013)을 작성하고 `alembic upgrade head`로 로컬 검증한다.
  2. Supabase 인스턴스와 로컬 DB 스키마를 비교하는 자동화 스크립트를 실행한다.
  3. QA 환경의 빈 DB에 마이그레이션을 적용하고 핵심 API Smoke 테스트를 수행한다.
  4. 결과 로그·마이그레이션 해시를 Phase 2 체크리스트에 첨부한다.
  5. 게이트 리뷰에서 승인받은 후 Phase 3 작업을 언블록한다.
- **기술 비교**

| 항목 | Alembic (현행) | SQLMesh 등 대안 |
| --- | --- | --- |
| 강점 | 기존 파이프라인과 호환, 러닝 커브 낮음 | 테스트 자동화·데이터 품질 관리 기능 풍부 |
| 약점 | 스키마 드리프트 감지 수동 | 초기 도입·러닝 커브 큼 |
| 적용 비용 | 낮음 | 높음 |
| 권장 판단 | 현 규모에서는 Alembic 유지 | 데이터 팀 확장 시 검토 |

- **산출물 & 오너**
  - 업데이트된 Alembic 스크립트 및 CI 검증 로그 (Backend Lead)
  - Phase 2 게이트 체크리스트 개정본 (Project Manager)
  - Smoke 테스트 리포트 (QA)

### 4.3 백그라운드 작업 아키텍처 확립

- **목적**: AI 일정 생성과 PDF 생성 같은 장시간 작업에 대해 SLA(30초)를 충족하고 실패 재처리를 자동화한다.
- **실행 워크플로**
  1. 요구사항을 바탕으로 큐/워커 스택(Celery+Redis, Dramatiq+RabbitMQ 등)을 선정한다.
  2. `POST /v1/travel-plans` 요청 시 작업을 큐에 등록하고 즉시 작업 ID를 반환하도록 API 계약을 업데이트한다.
  3. 작업 상태 저장소(예: Redis, Postgres) 구조를 정의하고 상태 전이(`pending → processing → completed/failed`)를 구현한다.
  4. 클라이언트는 `GET /v1/travel-plans/{id}/status` 폴링 또는 SSE/웹훅 구독 방식으로 결과를 수신하도록 설계한다.
  5. 재시도 정책, 모니터링 대시보드, 경보(예: Slack, PagerDuty)를 구성한다.
- **기술 비교**

| 항목 | Celery + Redis | Dramatiq + RabbitMQ | FastAPI BackgroundTasks |
| --- | --- | --- | --- |
| 강점 | 성숙한 생태계, 워커 모니터링 툴 풍부 | 경량, 타입 힌트 친화, 높은 처리량 | 간단히 도입 가능, 추가 인프라 불필요 |
| 약점 | 설정 복잡, 워커 관리 비용 | RabbitMQ 운영 필요 | 프로세스 재시작 시 작업 유실 위험 |
| 확장성 | 수평 확장 용이 | 중간 (RabbitMQ 클러스터 필요) | 낮음 (단일 노드) |
| 권장 판단 | SLA·재시도 중시 시 적합 | 중간 규모, 파이썬 생태계 유지 시 고려 | 프로토타입/POC 한정 |

- **산출물 & 오너**
  - 워커 인프라 IaC 정의(Terraform 등) (DevOps)
  - 상태 관리 스키마 및 API 계약 문서 (Backend Lead)
  - 클라이언트 폴링/SSE 구현 가이드 (Frontend Lead)

### 4.4 프론트엔드 런타임 안정화 전략

- **목적**: 프레임워크 RC 버전 의존으로 인한 예측 불가능한 회귀를 방지하고 안정적인 배포 파이프라인을 구축한다.
- **실행 워크플로**
  1. 기술 결정 회의에서 Next.js 14 LTS + React 18을 기본 런타임으로 확정하고 릴리스 노트 검토 결과를 기록한다.
  2. 핵심 사용자 플로우에 대한 MVP 테스트를 안정 버전에서 먼저 완료한다.
  3. Next.js 14 / React 19 평가용 PoC 브랜치를 만들고 호환성 이슈 리스트를 관리한다.
  4. 업그레이드 체크리스트(Vercel CLI, ESLint, Shadcn UI 호환성)를 작성해 전환 스프린트 준비를 한다.
  5. Stable 릴리스 이후 정해진 창구에서 프론트엔드 마이그레이션을 실행한다.
- **기술 비교**

| 항목 | Next.js 14 LTS + React 18 | Next.js 14 RC + React 19 |
| --- | --- | --- |
| 강점 | 검증된 생태계, 라이브러리 호환성 높음 | 최신 기능(PPR, 새로운 캐시) 즉시 활용 가능 |
| 약점 | 신기능 도입이 지연 | RC 불안정, 의존성 호환성 미확정 |
| CI/CD 안정성 | 높음 | 중간~낮음 (빌드 실패 위험) |
| 권장 판단 | MVP 및 초기 배포 | 실험/연구 브랜치에서 제한적으로 사용 |

- **산출물 & 오너**
  - 기술 결정 기록 및 체크리스트 (Frontend Lead)
  - PoC 결과 리포트 및 이슈 목록 (R&D Squad)
  - 전환 계획 및 릴리스 캘린더 (Project Manager)

### 4.5 PDF 생성 파이프라인 상세화

- **목적**: PDF 생성 기능을 백엔드와 일관되게 통합하여 배포·보안을 단순화하고 SLA(10초)를 준수한다.
- **실행 워크플로**
  1. PDF 생성 실행 환경을 결정한다(예: FastAPI 컨테이너 내 Playwright for Python).
  2. 템플릿 렌더링 로직, 지도 이미지 취득(Mapbox Static API), 자산 캐싱 전략을 설계한다.
  3. 생성된 PDF를 Supabase Storage/S3에 저장하고 만료 정책 및 접근 권한을 정의한다.
  4. 비동기 처리 여부를 결정하고, 작업 완료/실패 상태를 API 응답에 포함한다.
  5. 정기적인 파일 정리 작업과 비용 모니터링을 설정한다.
- **기술 비교**

| 항목 | Playwright for Python | Puppeteer (Node 서비스) | WeasyPrint |
| --- | --- | --- | --- |
| 강점 | FastAPI와 동일 런타임, async 지원 | 계획된 Node 파이프라인과 일치, 생태계 풍부 | 브라우저 의존 없음, 설치 간단 |
| 약점 | 헤드리스 브라우저 패키지 포함 필요 | 추가 Node 서비스 운영, 통신 계층 필요 | 복잡한 인터랙티브 UI 렌더링 한계 |
| 배포 단순성 | 중간 | 낮음 | 높음 |
| 권장 판단 | Python 백엔드 중심 구조에 적합 | 프론트엔드 팀이 Node 워크플로 관리 시 | 간단한 정적 PDF 요구 시 대체안 |

- **산출물 & 오너**
  - PDF 서비스 아키텍처 문서(시퀀스, 스토리지 정책) (Backend Lead)
  - 인프라 배포 스크립트 및 보안 설정 (DevOps)
  - 성능/품질 테스트 리포트 (QA)

---

## 5. 결론

현 설계는 사용자 가치와 기술 스택 측면에서 탄탄한 기반을 갖추고 있으나, 인증 통합, 마이그레이션 완료, 장시간 작업 처리 전략과 같은 핵심 운영 요소가 미비하다. 위 권장 사항을 조속히 반영하면 구현 단계에서의 리스크를 크게 줄이고 안정적인 MVP 전달이 가능할 것이다.
