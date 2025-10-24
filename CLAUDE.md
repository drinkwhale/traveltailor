# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**AI TravelTailor**: 개인 맞춤형 여행 일정을 30초 이내에 생성해주는 AI 기반 웹 애플리케이션입니다. FastAPI 백엔드(Python 3.11+)와 Next.js 14 프론트엔드(TypeScript 5.x)로 구성된 풀스택 애플리케이션으로, LangChain + OpenAI GPT-4o를 활용한 AI 여행 일정 생성, Google Places/Mapbox 연동, PDF 내보내기 등을 제공합니다.

## 아키텍처

### 모노레포 구조
```
backend/          FastAPI + SQLAlchemy + LangChain (Python 3.11+)
frontend/         Next.js 14 + React 18 + TypeScript 5.x
shared/           프론트엔드·백엔드 간 공유 타입/스키마
specs/            기능 명세, 구현 계획, 작업 목록
docs/             배포, 외부 API, 품질 관련 문서
```

### 백엔드 구조 (backend/src/)
- **api/v1/**: REST API 엔드포인트 (auth, travel_plans, preferences, recommendations, exports)
- **models/**: SQLAlchemy ORM 모델 (User, TravelPlan, DailyItinerary, Place, Route 등)
- **schemas/**: Pydantic 스키마 (요청/응답 검증)
- **services/**: 비즈니스 로직 계층
  - `ai/`: LangChain 기반 AI 파이프라인 (planner, preference_analyzer, timeline_generator, budget_allocator, cache)
  - `places/`: Google Places API 연동 장소 추천
  - `routes/`: Google Maps API 경로 최적화
  - `pdf/`: PDF 생성 (Playwright + Jinja2)
  - `exports/`: 일정 내보내기 (PDF, Google Calendar, Apple Wallet)
  - `recommendations/`: 항공편/숙박 추천 (Skyscanner, Booking.com)
- **integrations/**: 외부 API 클라이언트 (Google, Mapbox, OpenAI)
- **core/**: 핵심 유틸리티 (security, cache, csrf)
- **config/**: 설정 (database, settings)
- **middleware/**: CORS, CSRF, 보안 헤더, Rate Limiting
- **metrics/**: Prometheus 메트릭

### 프론트엔드 구조 (frontend/src/)
- **app/**: Next.js 14 App Router 기반 페이지
  - `(auth)/`: 인증된 사용자용 페이지 (create, plan, history, preferences)
  - `(public)/`: 공개 페이지 (login, signup)
- **components/**: React 컴포넌트
  - `forms/`: 여행 계획 생성 폼
  - `timeline/`: 일정 타임라인 뷰
  - `budget/`: 예산 요약
  - `map/`: Mapbox 지도
  - `pdf/`: PDF 프리뷰
  - `recommendations/`: 항공/숙박 추천
  - `ui/`: Shadcn UI 기반 공통 컴포넌트
- **lib/api/**: 백엔드 API 클라이언트 (axios 기반)
- **hooks/**: React Custom Hooks
- **types/**: TypeScript 타입 정의

## 주요 명령어

### 백엔드 (Python)
```bash
cd backend

# 환경 설정
uv venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# 데이터베이스 마이그레이션
uv run alembic upgrade head                           # 최신 마이그레이션 적용
uv run alembic revision --autogenerate -m "message"   # 새 마이그레이션 생성
uv run alembic downgrade -1                           # 롤백

# 개발 서버
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 코드 품질
uv run ruff check src/ tests/      # Lint
uv run black src/ tests/           # Format
uv run mypy src/                   # Type check
uv run pytest                      # Test (with coverage)
uv run pytest tests/unit/test_planner.py -v  # 단일 테스트 파일
```

### 프론트엔드 (TypeScript)
```bash
cd frontend

# 환경 설정
pnpm install                       # npm install도 가능
pnpm exec playwright install --with-deps

# 개발 서버
pnpm dev                           # http://localhost:3000

# 코드 품질
pnpm lint                          # ESLint
pnpm type-check                    # TypeScript 타입 검사
pnpm exec playwright test          # E2E 테스트

# 프로덕션 빌드
pnpm build
pnpm start
```

## 핵심 워크플로우

### AI 여행 일정 생성 파이프라인
1. **사용자 입력** → 프론트엔드 `TravelPlanForm` ([frontend/src/components/forms/TravelPlanForm.tsx](frontend/src/components/forms/TravelPlanForm.tsx))
2. **API 요청** → `POST /api/v1/travel-plans` ([backend/src/api/v1/travel_plans.py](backend/src/api/v1/travel_plans.py))
3. **AI 처리**:
   - `services/ai/planner.py`: 전체 파이프라인 오케스트레이션
   - `services/ai/preference_analyzer.py`: 사용자 선호도 분석 (LangChain + GPT-4o)
   - `services/ai/timeline_generator.py`: 시간대별 일정 생성
   - `services/ai/budget_allocator.py`: 예산 배분
   - `services/ai/cache.py`: Redis 기반 AI 응답 캐싱 (TTL 15분)
4. **장소 추천** → `services/places/recommender.py` (Google Places API)
5. **경로 최적화** → `services/routes/optimizer.py` (Google Maps API)
6. **DB 저장** → SQLAlchemy ORM (TravelPlan, DailyItinerary, ItineraryPlace, Route)
7. **응답 반환** → 프론트엔드 `DailyTimeline` 컴포넌트에서 시각화

### 인증 흐름
- **백엔드**: Supabase Auth + JWT ([backend/src/core/security.py](backend/src/core/security.py), [backend/src/api/v1/auth.py](backend/src/api/v1/auth.py))
- **프론트엔드**: React Query로 인증 상태 관리 ([frontend/src/lib/hooks/useAuth.ts](frontend/src/lib/hooks/useAuth.ts))
- **CSRF 보호**: `X-CSRF-Token` 헤더 + httpOnly 쿠키 ([backend/src/core/csrf.py](backend/src/core/csrf.py))

### 데이터베이스 마이그레이션 규칙
- **마이그레이션 작성 시 반드시**:
  1. 테스트 데이터베이스에서 드라이런 실행
  2. 롤백 전략 검증 (`alembic downgrade -1`)
  3. 마이그레이션 파일 검토 (auto-generated 코드 확인)
- **참고**: [backend/alembic/README.md](backend/alembic/README.md)

### 외부 API 연동
- **Google Places**: 장소 추천, 사진, 평점 ([backend/src/integrations/google_places.py](backend/src/integrations/google_places.py))
- **Google Maps**: 경로 최적화, 거리/시간 계산 ([backend/src/integrations/google_maps.py](backend/src/integrations/google_maps.py))
- **Mapbox**: 프론트엔드 지도 렌더링 ([frontend/src/components/map/](frontend/src/components/map/))
- **OpenAI**: LangChain을 통한 GPT-4o 호출 ([backend/src/services/ai/](backend/src/services/ai/))
- **캐싱**: Redis로 장소 검색 결과 15분, 항공편 5분 캐싱

## 보안 및 성능

### Rate Limiting (SlowAPI)
- 로그인/회원가입: 5회/분
- 전역: 100회/분
- 설정: [backend/src/api/dependencies.py](backend/src/api/dependencies.py)

### CSRF 보호
- 모든 state-changing 요청에 `X-CSRF-Token` 헤더 필수
- 토큰 발급: `GET /v1/csrf-token`
- 구현: [backend/src/core/csrf.py](backend/src/core/csrf.py), [backend/src/middleware/security_headers.py](backend/src/middleware/security_headers.py)

### 캐싱 전략
- **Redis**: AI 응답, 장소 검색, 항공편 검색 캐싱
- **PostGIS**: 공간 인덱스로 근접 검색 최적화
- **Service Worker**: 프론트엔드 오프라인 지원 (Cache First / Network First / Stale-While-Revalidate)

### 관측성 (Observability)
- **Sentry**: 에러 추적 (환경 변수: `SENTRY_DSN`, `NEXT_PUBLIC_SENTRY_DSN`)
- **PostHog**: 사용자 분석 (환경 변수: `POSTHOG_API_KEY`, `NEXT_PUBLIC_POSTHOG_KEY`)
- **Prometheus**: API 메트릭 (`/metrics` 엔드포인트)

## 커밋 및 PR 규칙

### 커밋 메시지
- **언어**: 한국어 (필요시 괄호로 영어 병기)
- **형식**: Conventional Commits (`fix:`, `feat:`, `refactor:`, `docs:`, `chore:` 등)
- **예시**:
  ```
  fix: PDF 생성 시 좌표 누락 처리 개선
  feat: 여행 선호도 분석 AI 파이프라인 추가
  refactor: 장소 추천 서비스 캐싱 로직 개선
  ```

### PR 작성
- **필수 포함 항목**:
  - 요약 (Summary)
  - 연관된 이슈/작업 링크 (specs/001-ai-travel-planner/tasks.md의 Task ID)
  - 검증 결과 (`uv run pytest` 또는 `pnpm lint` 출력)
  - 필요시 UI 스크린샷 또는 API 샘플
- **머지 전**: CI 통과 확인, 리뷰 요청
- **머지 방식**: 히스토리 선형 유지를 위해 리베이스 선호

## 환경 변수

### 백엔드 (.env)
```bash
# 앱/보안
APP_ENV=development
SECRET_KEY=...
JWT_SECRET_KEY=...

# 데이터베이스/Supabase
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...

# AI
OPENAI_API_KEY=...

# 외부 API
GOOGLE_MAPS_API_KEY=...
MAPBOX_ACCESS_TOKEN=...
AMADEUS_API_KEY=...
AMADEUS_API_SECRET=...

# 관측성 (선택)
SENTRY_DSN=...
POSTHOG_API_KEY=...
```

### 프론트엔드 (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=...

# 관측성 (선택)
NEXT_PUBLIC_SENTRY_DSN=...
NEXT_PUBLIC_POSTHOG_KEY=...
```

## 작업 관리

### 작업 목록 (tasks.md)
- **위치**: [specs/001-ai-travel-planner/tasks.md](specs/001-ai-travel-planner/tasks.md)
- **형식**: `[ID] [P?] [Story] 설명`
  - `[P]`: 병렬 실행 가능
  - `[Story]`: 사용자 스토리 (US1, US2, US3)
- **Phase 구조**:
  - Phase 1: 프로젝트 초기 설정
  - Phase 2: 기반 인프라 (DB, 인증)
  - Phase 3-8: 사용자 스토리별 기능 구현

### 개발 플로우
1. `specs/001-ai-travel-planner/spec.md` 확인 (요구사항)
2. `specs/001-ai-travel-planner/plan.md` 확인 (설계)
3. `specs/001-ai-travel-planner/tasks.md`에서 다음 작업 확인
4. Feature 브랜치 생성 (`feature/phase{N}-t{ID}`)
5. 코드 작성 + 테스트
6. Lint/Type check 통과 확인
7. 커밋 + PR 생성
8. CI 통과 + 리뷰 후 머지

## 코드 스타일

### Python (Backend)
- **Formatter**: Black (line-length=100)
- **Linter**: Ruff (E, W, F, I, B, C4)
- **Type Checker**: Mypy (strict mode)
- **설정**: [backend/pyproject.toml](backend/pyproject.toml)

### TypeScript (Frontend)
- **Linter**: ESLint (Next.js config)
- **Formatter**: Prettier
- **설정**: [frontend/.eslintrc.json](frontend/.eslintrc.json)

## 주요 참고 문서

- **기능 명세**: [specs/001-ai-travel-planner/spec.md](specs/001-ai-travel-planner/spec.md)
- **구현 계획**: [specs/001-ai-travel-planner/plan.md](specs/001-ai-travel-planner/plan.md)
- **작업 목록**: [specs/001-ai-travel-planner/tasks.md](specs/001-ai-travel-planner/tasks.md)
- **데이터 모델**: [specs/001-ai-travel-planner/data-model.md](specs/001-ai-travel-planner/data-model.md)
- **빠른 시작**: [README.md](README.md), [backend/README.md](backend/README.md), [frontend/README.md](frontend/README.md)

## 중요 규칙

1. **데이터베이스 스키마 변경 시 반드시 Alembic 마이그레이션 사용**
   - 직접 SQL 실행 금지
   - 마이그레이션 드라이런 → 롤백 검증 → 커밋

2. **외부 API 호출 시 반드시 에러 핸들링 및 폴백 로직 구현**
   - Tenacity로 재시도 로직 추가
   - 타임아웃 설정 (AI 파이프라인 30초 SLA)
   - 캐싱으로 API 호출 최소화

3. **AI 파이프라인 성능 SLA: 30초 이내 응답**
   - LangChain 스트리밍 + 비동기 처리
   - Redis 캐싱으로 반복 요청 최적화
   - Prometheus 메트릭으로 성능 모니터링

4. **보안 체크리스트**
   - 모든 state-changing API에 CSRF 토큰 검증
   - Rate limiting 설정 확인
   - SQL 인젝션 방지 (SQLAlchemy ORM 사용)
   - XSS 방지 (DOMPurify 사용)

5. **코드 품질**
   - 커밋 전 반드시 `ruff check`, `black`, `mypy` (백엔드) 또는 `pnpm lint`, `pnpm type-check` (프론트엔드) 실행
   - PR에 테스트 결과 포함
   - 복잡한 비즈니스 로직은 단위 테스트 작성

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
