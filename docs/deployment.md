# Deployment Guide

## Environment Configuration
- 샘플 파일
  - `backend/.env.example`: 기본 개발 템플릿. 프로덕션에서는 `APP_ENV=production`, `DEBUG=False`, `SESSION_COOKIE_DOMAIN`을 실 서비스 도메인으로 변경한다.
  - `backend/.env.production.example`: 운영용 설정 사본을 생성할 때 참고용으로 복사한다.
  - `frontend/.env.example`, `frontend/.env.production.example`: Vercel 및 로컬 개발에 필요한 공개 변수를 정의한다.
- 프로덕션에서는 모든 값을 비밀 관리(예: Vercel Secrets, Render/ Railway Variables, GitHub Secrets)에 저장한다.

## Backend (FastAPI)
1. **환경 변수**: `.env` 또는 호스팅 플랫폼 변수를 통해 데이터베이스, Redis, Sentry, PostHog, 외부 API 키 설정.
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
7. **배포 설정**:
   - Render: `backend/render.yaml` 블루프린트로 서비스 생성 → 자동 빌드/헬스체크/마이그레이션(`alembic upgrade head`) 적용.
   - Railway: `backend/railway.json`을 불러와 서비스 생성 → 배포 후 `alembic upgrade head`가 실행되도록 구성.
   - 수동 실행이 필요할 경우 `python backend/scripts/run_migrations.py`로 마이그레이션을 적용한다.

## Frontend (Next.js @ Vercel)
1. 환경 변수 (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SENTRY_DSN`, `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN`) → `vercel env` 또는 Vercel 대시보드에서 설정.
2. `frontend/vercel.json`으로 Vercel 프로젝트를 설정하면 빌드 명령, 보안 헤더, `/api/*` 백엔드 프록시를 일괄 관리할 수 있다.
3. 배포 후 `npm run build` 성공 여부를 확인하고 필요 시 `pnpm exec playwright test --project=chromium` 로 스모크 테스트.
4. Service Worker 등록 확인(`chrome://serviceworker-internals`).

## 공통 체크
- HSTS, CSP, Referrer-Policy 헤더 활성화.
- TLS 종단점에서 `Secure`, `SameSite` 쿠키 속성 확인.
- Prometheus `/metrics` 수집 → Alertmanager 규칙: `api_request_errors_total` p95 > 1% 알람.
- PostHog 이벤트 스트림에 `travel_plan_generated` 사용자 이벤트가 집계되는지 확인.

## CI/CD 권장
- `.github/workflows/ci.yml` 파이프라인이 백엔드 pytest, 프론트엔드 빌드 검증, Vercel/Render(또는 Railway) 웹훅 트리거, Alembic 마이그레이션 실행을 자동화한다.
- main 브랜치 머지 시 테스트 통과 필수.
- Render/Railway/DB 관련 토큰은 GitHub Secrets(`VERCEL_DEPLOY_HOOK`, `RENDER_DEPLOY_HOOK`, `RAILWAY_DEPLOY_HOOK`, `PRODUCTION_DATABASE_URL` 등)으로 관리한다.
- Docker 이미지 태그: `traveltailor/backend:<git-sha>`.
