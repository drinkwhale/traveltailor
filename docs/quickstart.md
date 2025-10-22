# TravelTailor Quickstart

## 1. 필수 전제
- Node.js 20+, pnpm 9 / npm 10
- Python 3.11, uv 패키지 매니저
- Docker (PostgreSQL + Redis 테스트용)
- OpenAI, Google Maps, Mapbox, Skyscanner API 키

## 2. 로컬 실행
```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 백엔드
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
uv run alembic upgrade head
uv run uvicorn src.main:app --reload

# 프론트엔드
cd ../frontend
pnpm install
pnpm exec playwright install --with-deps
pnpm dev
```

## 3. 보안 셋업
- `SENTRY_DSN`, `POSTHOG_API_KEY` 설정 시 관측 자동화
- TLS 적용 시 `SESSION_COOKIE_SECURE=true`
- 프론트엔드는 CSRF 토큰(`/v1/csrf-token`)을 자동으로 주입

## 4. 검증 체크리스트
1. 회원가입/로그인 후 httpOnly 쿠키와 `X-Response-Time` 헤더 확인
2. `/v1/travel-plans` POST → Redis 캐시 히트 로그(`backend/src/core/cache.py`) 확인
3. 오프라인 전환(DevTools) → 요청이 IndexedDB 큐에 저장되는지 확인
4. `pnpm exec playwright test` 로 로그인 플로우 E2E 검증

## 5. 자주 쓰는 명령어
```bash
# 백엔드 정적 분석/테스트
uv run ruff check
uv run pytest

# 프론트엔드 품질
pnpm lint
pnpm type-check

# 전체 스택(Docker)
docker-compose up --build
```
