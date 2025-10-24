# traveltailor 개발 가이드라인

AI TravelTailor - 개인 맞춤형 여행 일정을 30초 이내에 생성하는 AI 기반 웹 애플리케이션

최종 업데이트: 2025-10-23

## 프로젝트 한 줄 요약
FastAPI 백엔드와 Next.js 프론트엔드로 구성된 AI 기반 맞춤형 여행 일정 자동 생성 서비스 (OpenAI GPT-4o + LangChain + Supabase + Google Places + Mapbox)

## 현재 최우선 목표
Phase 8 완료 후 프로덕션 배포 준비 단계 - 성능·보안·오프라인·모니터링 체계 완성

## 활성 기술 스택

### Frontend
- **언어**: TypeScript 5.6.3
- **프레임워크**: Next.js 14.2.11, React 18.2.0
- **상태 관리**: React Query (@tanstack/react-query 5.59.20)
- **스타일링**: TailwindCSS 3.4.14, CVA (class-variance-authority 0.7.0)
- **지도**: Mapbox GL JS 3.7.0, react-map-gl 7.1.7
- **테스트**: Playwright 1.48.2
- **관측성**: Sentry 8.24.0, PostHog 1.132.3
- **패키지 매니저**: pnpm
- **Node 버전**: >=20.11.0

### Backend
- **언어**: Python 3.11+
- **프레임워크**: FastAPI 0.115.0, Uvicorn 0.32.0
- **ORM**: SQLAlchemy 2.0.36, Alembic 1.14.0
- **DB 드라이버**: asyncpg 0.30.0, psycopg2-binary 2.9.10
- **AI/ML**: LangChain 0.3.7, OpenAI 1.54.4, tiktoken 0.8.0
- **작업 큐**: Celery 5.4.0 with Redis
- **인증**: Supabase 2.9.0, python-jose 3.3.0, passlib 1.7.4
- **보안**: fastapi-csrf-protect 0.3.4, itsdangerous 2.2.0, SlowAPI 0.1.9
- **외부 API**: googlemaps 4.10.0, requests 2.32.3, httpx 0.27.2
- **PDF 생성**: PyPDF2 3.0.1, Playwright 1.48.0
- **템플릿**: Jinja2 3.1.4
- **관측성**: Sentry 2.16.0, PostHog 3.5.0, Prometheus 0.21.0
- **캐싱**: Redis 5.0.8
- **테스트**: pytest 8.3.3, pytest-asyncio 0.24.0, pytest-cov 6.0.0
- **코드 품질**: black 24.10.0, ruff 0.7.4, mypy 1.13.0
- **패키지 관리**: uv (pip-tools 대체)

### 데이터베이스
- **Primary DB**: Supabase PostgreSQL 15 (PostGIS 확장)
- **캐싱**: Redis 5.0.8

### 외부 서비스
- **AI**: OpenAI GPT-4o (LangChain 통합)
- **지도/장소**: Google Places API, Mapbox
- **항공/숙박**: Skyscanner API, Booking.com Affiliate, Agoda API
- **모니터링**: Sentry, PostHog

## 프로젝트 구조

```
traveltailor/
├── backend/                  # FastAPI 백엔드
│   ├── src/
│   │   ├── api/             # API 엔드포인트 (인증, 여행, 장소, 숙박, 항공, CSRF)
│   │   ├── config/          # 환경 설정 (DB, Redis, Celery, 외부 API)
│   │   ├── core/            # 핵심 비즈니스 로직 (AI 에이전트, 여행 플래너)
│   │   ├── integrations/    # 외부 API 연동 (Google Places, OpenAI, Skyscanner 등)
│   │   ├── metrics/         # Prometheus 메트릭
│   │   ├── middleware/      # 미들웨어 (CORS, 에러 핸들링, 레이트 리미팅)
│   │   ├── models/          # SQLAlchemy 모델 (User, Trip, Place, Accommodation 등)
│   │   ├── schemas/         # Pydantic 스키마 (요청/응답 검증)
│   │   ├── services/        # 서비스 레이어 (인증, 여행, PDF 생성)
│   │   ├── utils/           # 유틸리티 (로깅, 보안, 검증)
│   │   └── main.py          # FastAPI 애플리케이션 진입점
│   ├── alembic/             # DB 마이그레이션
│   ├── tests/               # pytest 테스트 스위트
│   └── pyproject.toml       # Python 의존성 및 도구 설정
├── frontend/                 # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/             # Next.js 14 App Router (페이지, 레이아웃)
│   │   ├── components/      # React 컴포넌트 (UI, 지도, 폼)
│   │   ├── hooks/           # 커스텀 훅 (API, 인증, 지도)
│   │   ├── lib/             # 유틸리티 및 헬퍼
│   │   └── services/        # API 클라이언트 (axios 기반)
│   ├── public/              # 정적 에셋, Service Worker, Manifest
│   ├── tests/               # Playwright E2E 테스트
│   ├── package.json         # Node 의존성 및 스크립트
│   └── tsconfig.json        # TypeScript 설정
├── shared/                   # 프론트엔드·백엔드 공유 타입/스키마
│   └── types/               # 공통 TypeScript 타입 정의
├── docs/                     # 기술 문서
│   ├── external-apis.md     # 외부 API 연동 가이드
│   ├── deployment.md        # 배포 절차 및 CI/CD
│   └── architecture-analysis-report.md  # 아키텍처 분석
├── specs/                    # 기능 명세 및 계획
│   └── 001-ai-travel-planner/
│       ├── spec.md          # 기능 명세 (User Story, Acceptance Scenario)
│       ├── plan.md          # 구현 계획 (Phase별 작업)
│       └── tasks.md         # 작업 목록 (T001~T155)
└── README.md                 # 프로젝트 개요 및 빠른 시작

## 주요 명령어

### Backend
```bash
cd backend
uv venv                           # 가상환경 생성
source .venv/bin/activate         # 가상환경 활성화 (Windows: .venv\Scripts\activate)
uv pip install -e ".[dev]"        # 의존성 설치 (개발 도구 포함)
uv run alembic upgrade head       # DB 마이그레이션 적용
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000  # 개발 서버 실행

# 테스트 & 코드 품질
uv run pytest                     # 전체 테스트 실행
uv run pytest tests/test_auth.py  # 특정 테스트 파일 실행
uv run ruff check src/ tests/     # Linting (자동 수정: ruff check --fix)
uv run black src/ tests/          # 포맷팅
uv run mypy src/                  # 타입 체킹
```

### Frontend
```bash
cd frontend
pnpm install                      # 의존성 설치
pnpm exec playwright install --with-deps  # Playwright 브라우저 설치
pnpm dev                          # 개발 서버 실행 (http://localhost:3000)
pnpm build                        # 프로덕션 빌드
pnpm start                        # 프로덕션 서버 실행

# 테스트 & 코드 품질
pnpm lint                         # ESLint 실행
pnpm type-check                   # TypeScript 타입 체킹
pnpm exec playwright test         # E2E 테스트 실행
```

### 전체 프로젝트
```bash
# Git 워크플로우
git checkout -b feature/your-feature-name  # 기능 브랜치 생성
git add .
git commit -m "feat: 새로운 기능 추가"     # Conventional Commits 패턴
git push origin feature/your-feature-name
# GitHub에서 PR 생성 → CI 통과 확인 → 리뷰 → 머지
```

## 핵심 로직 및 파일

### Backend 주요 파일
- **[backend/src/main.py](backend/src/main.py)**: FastAPI 애플리케이션 진입점, 미들웨어·라우터 설정, Sentry/PostHog 초기화
- **[backend/src/core/travel_planner.py](backend/src/core/travel_planner.py)**: AI 여행 일정 생성 핵심 로직 (LangChain + OpenAI GPT-4o)
- **[backend/src/integrations/openai_integration.py](backend/src/integrations/openai_integration.py)**: OpenAI API 연동 (LangChain 에이전트)
- **[backend/src/integrations/google_places_integration.py](backend/src/integrations/google_places_integration.py)**: Google Places API 연동 (장소 검색, 상세 정보)
- **[backend/src/services/auth_service.py](backend/src/services/auth_service.py)**: 인증 서비스 (회원가입, 로그인, JWT 토큰 발급)
- **[backend/src/services/trip_service.py](backend/src/services/trip_service.py)**: 여행 일정 CRUD 및 비즈니스 로직
- **[backend/src/services/pdf/generator.py](backend/src/services/pdf/generator.py)**: PDF 생성 로직 (Playwright 기반 HTML-to-PDF)
- **[backend/src/middleware/rate_limit.py](backend/src/middleware/rate_limit.py)**: SlowAPI 기반 레이트 리미팅 (로그인 5회/분, 글로벌 100회/분)
- **[backend/src/middleware/security.py](backend/src/middleware/security.py)**: CSRF 보호, XSS 방어, 보안 헤더
- **[backend/src/models/trip.py](backend/src/models/trip.py)**: SQLAlchemy Trip 모델 (여행 일정 메타데이터)
- **[backend/src/models/place.py](backend/src/models/place.py)**: Place 모델 (관광지, 식당 등 장소 정보, PostGIS 공간 인덱스)
- **[backend/alembic/versions/](backend/alembic/versions/)**: DB 마이그레이션 히스토리

### Frontend 주요 파일
- **[frontend/src/app/page.tsx](frontend/src/app/page.tsx)**: 메인 페이지 (여행 조건 입력 폼)
- **[frontend/src/app/itinerary/[id]/page.tsx](frontend/src/app/itinerary/[id]/page.tsx)**: 여행 일정 상세 페이지
- **[frontend/src/components/ItineraryForm.tsx](frontend/src/components/ItineraryForm.tsx)**: 여행 조건 입력 폼 컴포넌트
- **[frontend/src/components/MapView.tsx](frontend/src/components/MapView.tsx)**: Mapbox 지도 컴포넌트 (경로 시각화)
- **[frontend/src/components/ItineraryTimeline.tsx](frontend/src/components/ItineraryTimeline.tsx)**: 일정 타임라인 컴포넌트
- **[frontend/src/hooks/useItinerary.ts](frontend/src/hooks/useItinerary.ts)**: React Query 기반 일정 API 훅
- **[frontend/src/hooks/useAuth.ts](frontend/src/hooks/useAuth.ts)**: 인증 상태 관리 훅
- **[frontend/src/services/api.ts](frontend/src/services/api.ts)**: Axios 기반 API 클라이언트 (인터셉터, CSRF 토큰 자동 처리)
- **[frontend/src/lib/offline.ts](frontend/src/lib/offline.ts)**: 오프라인 지원 (Service Worker + IndexedDB 큐)
- **[frontend/public/sw.js](frontend/public/sw.js)**: Service Worker (캐시 전략: Cache First / Network First / Stale-While-Revalidate)

## 로컬 실행 및 테스트 방법

### 환경 설정
1. **리포지토리 클론**
   ```bash
   git clone https://github.com/drinkwhale/traveltailor.git
   cd traveltailor
   ```

2. **환경 변수 설정**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # 필수: DATABASE_URL, SUPABASE_URL/KEY, OPENAI_API_KEY, JWT_SECRET_KEY
   # 선택: GOOGLE_PLACES_API_KEY, MAPBOX_TOKEN, SENTRY_DSN, POSTHOG_API_KEY

   # Frontend
   cp frontend/.env.local.example frontend/.env.local
   # 필수: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_MAPBOX_TOKEN
   # 선택: NEXT_PUBLIC_SENTRY_DSN, NEXT_PUBLIC_POSTHOG_KEY
   ```

3. **백엔드 실행**
   ```bash
   cd backend
   uv venv && source .venv/bin/activate
   uv pip install -e ".[dev]"
   uv run alembic upgrade head
   uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **프론트엔드 실행**
   ```bash
   cd frontend
   pnpm install
   pnpm exec playwright install --with-deps
   pnpm dev  # http://localhost:3000
   ```

### 테스트 실행
- **Backend**: `cd backend && uv run pytest`
- **Frontend**: `cd frontend && pnpm lint && pnpm type-check && pnpm exec playwright test`

## 코드 스타일

### Backend (Python)
- **포맷팅**: Black (line-length=100)
- **Linting**: Ruff (pycodestyle, pyflakes, isort, flake8-bugbear)
- **타입 체킹**: mypy (strict mode)
- **실행**: `uv run black src/ tests/ && uv run ruff check src/ tests/ && uv run mypy src/`

### Frontend (TypeScript)
- **포맷팅**: Prettier (내장)
- **Linting**: ESLint (eslint-config-next)
- **타입 체킹**: TypeScript strict mode
- **실행**: `pnpm lint && pnpm type-check`

## 중요 규칙 및 제약사항

### 보안
1. **CSRF 보호**: 모든 POST/PUT/DELETE 요청에 `X-CSRF-Token` 헤더 필수 ([frontend/src/services/api.ts:52](frontend/src/services/api.ts#L52))
2. **레이트 리미팅**: 로그인/회원가입 5회/분, 그 외 100회/분 ([backend/src/middleware/rate_limit.py:15](backend/src/middleware/rate_limit.py#L15))
3. **환경 변수 검증**: `.env` 파일의 시크릿 키는 절대 커밋하지 말 것 (`.gitignore`에 `.env` 포함 확인)

### 데이터베이스
1. **마이그레이션**: DB 스키마 변경 시 반드시 Alembic 사용 (`uv run alembic revision --autogenerate -m "message"`)
2. **공간 인덱스**: Place 모델의 `coordinates` 필드는 PostGIS GIST 인덱스 사용 ([backend/src/models/place.py:18](backend/src/models/place.py#L18))
3. **캐싱 전략**: Google Places 결과는 Redis에 15분 TTL, 항공편은 5분 TTL ([backend/src/integrations/google_places_integration.py:87](backend/src/integrations/google_places_integration.py#L87))

### AI/ML
1. **프롬프트 관리**: LangChain 프롬프트 템플릿은 [backend/src/core/travel_planner.py:45](backend/src/core/travel_planner.py#L45)에서 중앙 관리
2. **토큰 제한**: OpenAI API 요청당 최대 4096 토큰 (tiktoken으로 사전 검증)
3. **Fallback**: AI 생성 실패 시 캐시된 템플릿 일정 반환 ([backend/src/services/trip_service.py:123](backend/src/services/trip_service.py#L123))

### 프론트엔드
1. **API 응답 검증**: 모든 API 응답은 Zod 스키마로 검증 ([frontend/src/services/api.ts:102](frontend/src/services/api.ts#L102))
2. **지도 토큰**: Mapbox 토큰은 환경 변수에서만 로드, 하드코딩 금지
3. **오프라인 지원**: Service Worker 캐시 우선순위: 정적 에셋(Cache First) → API(Network First) → 폴백(Stale-While-Revalidate)

### 모니터링
1. **Sentry**: 에러 발생 시 자동 리포팅 (DSN 설정 필수)
2. **PostHog**: 사용자 행동 이벤트 자동 추적 (개인정보 마스킹 적용)
3. **Prometheus**: `/metrics` 엔드포인트에서 메트릭 노출 ([backend/src/metrics/prometheus.py](backend/src/metrics/prometheus.py))

## 커밋 및 PR 지침
- **커밋 메시지 언어**: 한국어로 작성 (필요한 경우 괄호로 영어 병기 가능)
- **커밋 메시지 형식**: Conventional Commits 패턴 사용
  - `feat:` 새로운 기능 추가
  - `fix:` 버그 수정
  - `refactor:` 코드 리팩토링 (동작 변경 없음)
  - `docs:` 문서 수정
  - `test:` 테스트 추가/수정
  - `chore:` 빌드, 설정 변경
  - 예: `fix: PDF 생성 시 좌표 누락 처리 개선`, `feat: 오프라인 지원 추가`
- **커밋 메시지 작성**: 간결하게 유지하고, 추가 맥락이 필요하면 본문에 한국어 설명 추가
- **PR 작성**:
  - 요약 (변경 사항, 동기, 영향 범위)
  - 연관된 이슈 링크 (예: `Closes #123`)
  - 검증 결과 (`uv run pytest` 또는 `pnpm test` 출력 캡처)
  - 필요시 UI 스크린샷 또는 API 샘플 JSON 첨부
- **머지 전**: CI 통과 확인, 코드 리뷰 승인 받기
- **머지 방식**: 히스토리 선형 유지를 위해 Squash & Merge 또는 Rebase 선호

## 최근 변경사항
- **2025-10-23**: Phase 8 완료 - 성능·보안·오프라인·모니터링 체계 구축
  - T151: Redis 캐싱 + PostGIS 공간 인덱스 (Place 검색 50% 속도 향상)
  - T152: SlowAPI 레이트 리미팅 + CSRF 보호 강화
  - T153: Service Worker + IndexedDB 오프라인 지원
  - T154: Sentry + PostHog + Prometheus 통합
  - T155: CI/CD 파이프라인 (GitHub Actions) 및 배포 자동화

## 모듈별 가이드
프로젝트가 복잡해지면 각 서브디렉토리(모듈)는 자신만의 컨텍스트와 규칙을 가집니다.

**규칙**: 특정 서브디렉토리의 파일을 사용하거나 읽어야 할 때, 작업을 시작하기 전 해당 디렉토리 내 `claude.md` 또는 `README.md` 파일을 먼저 확인하고 그 컨텍스트를 최우선으로 적용할 것.

- **[backend/src/api/claude.md](backend/src/api/claude.md)** (향후 추가 예정): API 라우터 레이어 규칙
- **[backend/src/core/claude.md](backend/src/core/claude.md)** (향후 추가 예정): 핵심 비즈니스 로직 규칙
- **[frontend/src/components/claude.md](frontend/src/components/claude.md)** (향후 추가 예정): UI 컴포넌트 작성 규칙

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
