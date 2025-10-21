# Implementation Plan: AI TravelTailor - 개인 맞춤형 여행 설계 서비스

**Branch**: `001-ai-travel-planner` | **Date**: 2025-10-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-travel-planner/spec.md`

## Summary

AI TravelTailor는 사용자의 여행 조건(목적지, 기간, 예산, 선호사항)을 입력받아 AI가 최적화된 전체 여행 일정을 자동으로 생성하는 서비스입니다. 웹 애플리케이션으로 시작하지만, 향후 네이티브 모바일 앱으로의 확장을 고려하여 설계됩니다.

핵심 기능:
- AI 기반 여행 일정 자동 생성 (30초 이내)
- 지도 기반 경로 시각화 및 외부 지도 앱 연동
- PDF 여행 일정표 생성 및 다운로드
- 항공편/숙박 예약 링크 제공
- 사용자 맞춤 학습 및 히스토리 관리

기술 접근:
- 프론트엔드: Next.js 14 + React 18 LTS (Progressive Web App 지원, 안정 버전 우선)
- 백엔드: FastAPI + Python 3.11 (RESTful API로 모바일 앱과 공유 가능)
- AI 엔진: LangChain + OpenAI GPT-4o (비동기 파이프라인, 캐시/폴백 포함)
- 데이터베이스: Supabase (PostgreSQL + 인증)
- 지도: Mapbox GL JS (웹과 네이티브 SDK 모두 지원)
- PDF: Puppeteer (Node.js)

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, Node.js 20.11+, Next.js 14, React 18
- Backend: Python 3.11+
- Mobile Future: React Native 준비 (코드 재사용을 위한 공유 로직 구조)

**Primary Dependencies**:
- Frontend: Next.js 14, React 18, Tailwind CSS, Shadcn UI, React Query, Mapbox GL JS
- Backend: FastAPI, LangChain, OpenAI SDK, Pydantic v2, SQLAlchemy, Redis (task queue + cache)
- PDF: Puppeteer, Mapbox Static API
- Mobile Ready: API-first 설계로 React Native 앱에서 동일 백엔드 사용 가능

**Storage**:
- Database: Supabase (PostgreSQL 15+)
- Auth: Supabase Auth (JWT, email, OAuth)
- Files: Supabase Storage (PDFs)
- Cache: Redis (optional, for API response caching)

**Testing**:
- Frontend: Jest, React Testing Library, Playwright (E2E)
- Backend: pytest, pytest-asyncio
- API: Supertest, OpenAPI validation
- Mobile Future: React Native Testing Library, Detox

**Target Platform**:
- Primary: Web (responsive, mobile-first design)
- Future: iOS 15+ and Android 10+ via React Native
- PWA: Progressive Web App 지원 (offline capability, installable)

**Project Type**: Web application (프론트엔드 + 백엔드 분리, RESTful API)

**Performance Goals**:
- AI 여행 일정 생성: <30초
- 지도 렌더링: <3초 (모든 마커 및 경로 표시)
- PDF 생성: <10초
- API 응답 시간: <200ms (p95)
- 동시 사용자 처리: 100+ concurrent requests

**Constraints**:
- 예산 범위 내 일정 생성 (±10% 허용)
- 외부 API 의존성 관리 (Google Places, Mapbox, 항공/숙박 API 레이트 리밋 및 장애 대응)
- 모바일 데이터 사용 최소화 (향후 앱 대비)
- GDPR 및 국내 개인정보보호법 준수 (사용자 데이터 암호화, 삭제 권리)
- 한국어/영어 다국어 지원
- 필수 외부 서비스와의 상용 계약 및 API 키/쿼터 확보가 완료되어야 개발을 진행할 수 있음
- AI 비용 한도(일 $50, 월 $1,200) 초과 시 폴백 모드를 자동 전환

**Scale/Scope**:
- MVP: 100-1000 users
- 5 user stories (P1-P3 우선순위)
- 20 functional requirements
- 9 core entities
- 15+ REST API endpoints
- Future: 10k+ users (mobile app launch 시)

**Mobile App Strategy** (향후 개발):

웹앱을 네이티브 앱으로 전환하는 2단계 접근:

**Phase 1: PWA (Progressive Web App)** - 즉시 적용
- next-pwa를 사용하여 웹앱을 설치 가능한 PWA로 변환
- iOS/Android 홈 화면에 추가 가능
- 오프라인 지원: Service Worker로 지도 타일, API 응답, PDF 캐싱
- 푸시 알림 준비 (Android 완전 지원, iOS 제한적)
- 추가 개발 비용 없이 앱 경험 제공

**Phase 2: Capacitor (필요 시)** - 앱스토어 배포
- 기존 Next.js/React 코드를 거의 그대로 iOS/Android 네이티브 앱으로 변환
- 앱스토어 (App Store, Google Play) 배포 가능
- 네이티브 기능 접근: 카메라, GPS, 파일시스템, 공유 등
- WebView 기반이지만 우수한 성능
- React Native 대비 장점: 웹 코드 재사용률 95%+, 학습 곡선 낮음

**설계 원칙** (모바일 전환 대비):
- API-First 아키텍처: 모든 비즈니스 로직을 백엔드 REST API로 구현
- 반응형 디자인: Mobile-first CSS로 모바일 UX 우선 개발
- 공유 타입: TypeScript interfaces를 백엔드와 공유
- Deep linking 준비: URL 스키마로 카카오맵/구글맵 연동
- 오프라인 데이터: IndexedDB로 여행 일정 로컬 저장

## Risk Mitigation & Operational Considerations

- **AI 파이프라인 안정화**: OpenAI 호출은 비동기 태스크 큐에서 실행하고, 30초 초과 시 규칙 기반 템플릿으로 폴백한다. 성공/실패 메트릭을 Prometheus로 수집한다.
- **외부 API 비용/쿼터 관리**: Google Places, Mapbox, 항공/숙박 API에 대해 예상 호출량 기반 비용 계산을 문서화하고, Redis 캐시와 지오해싱으로 중복 호출을 줄인다.
- **레이트 리밋 및 오류 처리**: 백엔드에서 per-user/per-IP 레이트 리밋을 적용하고, 외부 API 장애 시 사용자에게 명확한 상태 메시지를 제공한다.
- **데이터 보호**: Supabase Auth 세션과 사용자 데이터은 at-rest/ in-transit 암호화, 삭제 요청 SLA 7일 이내 처리.
- **기술 스택 업그레이드 전략**: Next.js 15, React 19 등 실험적 버전은 MVP 이후 별도 스파이크에서 검토하고, 호환성 검증 전까지는 LTS 버전을 유지한다.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: No constitution file found (template only)

**Evaluation**: ✅ PASS - No constraints defined, proceeding with best practices

**Notes**:
- Constitution이 정의되지 않았으므로 일반적인 소프트웨어 개발 모범 사례를 따릅니다
- 향후 프로젝트 원칙이 정의되면 재검토가 필요합니다

## Project Structure

### Documentation (this feature)

```
specs/001-ai-travel-planner/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Technical research (complete)
├── data-model.md        # Data model design (complete)
├── quickstart.md        # Developer guide (complete)
├── contracts/           # API contracts (to be created)
│   └── api-spec.yaml    # OpenAPI 3.0 specification
├── checklists/          # Quality checklists
│   └── requirements.md  # Requirements validation
└── tasks.md             # Implementation tasks (created by /speckit.tasks)
```

### Source Code (repository root)

```
# Web Application Structure (Backend + Frontend separation)

backend/
├── src/
│   ├── main.py                    # FastAPI application entry
│   ├── config/
│   │   ├── settings.py            # Environment configuration
│   │   └── database.py            # Database connection
│   ├── models/                    # SQLAlchemy models
│   │   ├── user.py
│   │   ├── travel_plan.py
│   │   ├── daily_itinerary.py
│   │   ├── place.py
│   │   └── ...
│   ├── schemas/                   # Pydantic schemas (request/response)
│   │   ├── travel_plan.py
│   │   ├── user.py
│   │   └── ...
│   ├── services/                  # Business logic
│   │   ├── ai_planner.py          # LangChain + GPT-4 integration
│   │   ├── place_service.py       # Google Places API integration
│   │   ├── flight_service.py      # Skyscanner API integration
│   │   ├── accommodation_service.py
│   │   └── ...
│   ├── api/                       # REST API endpoints
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── travel_plans.py
│   │   │   ├── places.py
│   │   │   └── users.py
│   │   └── dependencies.py        # Shared dependencies
│   └── utils/
│       ├── auth.py                # JWT utilities
│       ├── errors.py              # Custom exceptions
│       └── validators.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic/                       # Database migrations
├── requirements.txt
└── README.md

frontend/
├── src/
│   ├── app/                       # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx               # Home page
│   │   ├── plan/
│   │   │   ├── create/            # Travel plan creation
│   │   │   ├── [id]/              # View travel plan
│   │   │   └── history/           # User history
│   │   └── auth/
│   │       ├── login/
│   │       └── signup/
│   ├── components/                # React components
│   │   ├── ui/                    # Shadcn UI components
│   │   ├── travel/
│   │   │   ├── PlanForm.tsx
│   │   │   ├── DailyItinerary.tsx
│   │   │   ├── MapView.tsx
│   │   │   └── PDFPreview.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Footer.tsx
│   ├── lib/                       # Utilities and hooks
│   │   ├── api/                   # API client
│   │   │   ├── client.ts          # Axios instance
│   │   │   ├── travel-plans.ts
│   │   │   └── auth.ts
│   │   ├── hooks/
│   │   │   ├── useTravelPlan.ts
│   │   │   ├── useAuth.ts
│   │   │   └── useMap.ts
│   │   └── utils/
│   │       ├── date.ts
│   │       └── currency.ts
│   ├── styles/
│   │   └── globals.css
│   └── types/                     # TypeScript types
│       ├── api.ts                 # API response types
│       └── models.ts              # Domain models
├── public/
│   ├── icons/
│   └── images/
├── tests/
│   ├── unit/
│   └── e2e/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md

shared/
├── types/                         # Shared TypeScript types
│   └── common.ts                  # Types shared between frontend/backend
└── schemas/                       # JSON schemas for mobile
    └── api-contracts.json         # Auto-generated from OpenAPI spec

# Future Mobile Structure (준비)
# mobile/ (React Native - to be created later)
# ├── ios/
# ├── android/
# ├── src/
# │   ├── screens/
# │   ├── components/
# │   ├── services/                # Reuse backend API client logic
# │   └── types/                   # Import from shared/types
# └── package.json
```

**Structure Decision**:

웹 애플리케이션 구조(Backend + Frontend 분리)를 선택했습니다:

1. **Backend (FastAPI + Python)**: RESTful API 서버로, AI 여행 계획 생성 로직과 외부 API 통합을 담당합니다. 모바일 앱이 추가될 때도 동일한 API를 재사용할 수 있도록 설계되었습니다.

2. **Frontend (Next.js + React)**: 서버 사이드 렌더링과 정적 생성을 지원하는 모던 웹 애플리케이션입니다. Progressive Web App(PWA) 기능을 추가하여 모바일 경험을 개선하고, 향후 React Native로 전환 시 컴포넌트 로직을 재사용할 수 있습니다.

3. **Shared**: 프론트엔드와 백엔드 간 공유되는 타입 정의 및 스키마를 관리합니다. 향후 모바일 앱에서도 동일한 타입을 사용할 수 있도록 준비되어 있습니다.

4. **모바일 대비 설계**:
   - API-First 아키텍처: 모든 비즈니스 로직을 백엔드 API에 구현하여 웹과 모바일이 동일한 기능을 사용
   - 반응형 디자인: 모바일 우선(Mobile-first) 접근으로 웹에서 모바일 UX 검증
   - PWA 기능: 오프라인 지원, 푸시 알림 등을 웹에서 먼저 테스트
   - 공유 타입: TypeScript 타입을 JSON Schema로 변환하여 모바일에서 재사용

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

N/A - No constitution violations.

---

**Phase 0 (Research)**: ✅ Complete - [research.md](./research.md)
**Phase 1 (Design)**: In Progress - data-model.md (complete), contracts/ (pending), quickstart.md (complete), agent context update (pending)
**Phase 2 (Tasks)**: ✅ Complete - [tasks.md](./tasks.md) generated 2025-10-20

---

**Next Steps**:
1. Finalize database migration scripts for `users` and `user_preferences` tables (Alembic `versions/`).
2. Produce OpenAPI specification in `contracts/api-spec.yaml` and sync shared TypeScript types.
3. Validate external API contracts (Google Places, Mapbox, 항공/숙박 공급자) and document rate limits/cost guardrails.
4. Define AI pipeline performance/cost test plan (timeout handling, fallback coverage) before US1 implementation.
