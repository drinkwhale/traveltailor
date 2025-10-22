# Deployment Guide

## Backend (FastAPI)
1. **환경 변수**: `.env`에 데이터베이스, Redis, Sentry, PostHog, 외부 API 키 설정.
2. **빌드**:
   ```bash
   uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```
3. **Gunicorn 예시**:
   ```bash
   gunicorn src.main:app \
     --bind 0.0.0.0:8000 \
     --worker-class uvicorn.workers.UvicornWorker \
     --workers 4
   ```
4. **PostgreSQL**: PostGIS 확장 설치 (`CREATE EXTENSION postgis`).
5. **Redis**: `REDIS_URL` 노출, 보안 그룹/방화벽으로 제한.
6. **헬스 체크**: `/health` GET 사용. Rate limiting 429 응답 처리 필요.

## Frontend (Next.js @ Vercel)
1. 환경 변수 (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SENTRY_DSN`, `NEXT_PUBLIC_POSTHOG_KEY`).
2. `next.config.js`에 이미지 도메인, CSP 헤더 검토.
3. 배포 후 `pnpm exec playwright test --project=chromium` 로 스모크 테스트.
4. Service Worker 등록 확인(`chrome://serviceworker-internals`).

## 공통 체크
- HSTS, CSP, Referrer-Policy 헤더 활성화.
- TLS 종단점에서 `Secure`, `SameSite` 쿠키 속성 확인.
- Prometheus `/metrics` 수집 → Alertmanager 규칙: `api_request_errors_total` p95 > 1% 알람.
- PostHog 이벤트 스트림에 `travel_plan_generated` 사용자 이벤트가 집계되는지 확인.

## CI/CD 권장
- GitHub Actions → `backend/` lint + tests, `frontend/` lint + tests, Playwright smoke.
- main 브랜치 머지 시 테스트 통과 필수.
- Docker 이미지 태그: `traveltailor/backend:<git-sha>`.
