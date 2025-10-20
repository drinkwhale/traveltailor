# 🏗️ TravelTailor 프로젝트 아키텍처 분석 보고서

**작성일**: 2025-10-20
**분석 대상**: Phase 2 (T009-T031) 완료 시점
**작성자**: Architecture Review

---

## 📋 실행 요약

**프로젝트**: AI TravelTailor - 개인 맞춤형 여행 설계 서비스
**아키텍처 스타일**: 프론트엔드-백엔드 분리 (RESTful API)
**진행 상황**: Phase 2 (기반 인프라) 부분 완료 (T009-T031 중 T013 제외 완료)
**전반적 평가**: ✅ **양호 (Good)** - 견고한 기반, 몇 가지 개선 권장사항 있음

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [백엔드 아키텍처 분석](#2-백엔드-아키텍처-분석)
3. [프론트엔드 아키텍처 분석](#3-프론트엔드-아키텍처-분석)
4. [보안 및 인증 플로우](#4-보안-및-인증-플로우)
5. [확장성 및 성능](#5-확장성-및-성능)
6. [코드 품질 및 개발 경험](#6-코드-품질-및-개발-경험)
7. [의존성 관리 및 배포](#7-의존성-관리-및-배포)
8. [모바일 준비도](#8-모바일-준비도)
9. [문제점 및 위험 요소](#9-문제점-및-위험-요소)
10. [권장 개선 로드맵](#10-권장-개선-로드맵)
11. [최종 평가](#11-최종-평가)
12. [결론 및 권장사항](#12-결론-및-권장사항)

---

## 1. 아키텍처 개요

### 1.1 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 15)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Pages      │  │  Components  │  │    Hooks     │      │
│  │  (App Router)│  │  (Shadcn UI) │  │  (useAuth)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  API Client  │  │   Supabase   │                         │
│  │   (Axios)    │  │  Auth Client │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            ↕ REST API (JWT)
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Python 3.11)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  API Routes  │  │   Services   │  │  Integration │      │
│  │  (v1/auth)   │  │   (AI, etc)  │  │  (Maps, AI)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │    Models    │  │  Security    │                         │
│  │ (SQLAlchemy) │  │    (JWT)     │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              Database & External Services                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Supabase    │  │  Google Maps │  │   OpenAI     │      │
│  │  (Postgres)  │  │  Places API  │  │  (GPT-4)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 기술 스택 검증

**✅ 잘 선택된 부분**:
- FastAPI + Python 3.11: AI/ML 통합에 적합
- Next.js 15 + React 19: 최신 웹 프레임워크
- Supabase: 빠른 MVP 개발, Auth + DB 통합
- SQLAlchemy + Alembic: 성숙한 ORM + 마이그레이션
- TypeScript: 타입 안전성

**⚠️ 주의 필요**:
- React 19 RC 버전 사용 (프로덕션 배포 전 안정화 버전 대기 권장)
- Mapbox 설정 확인 필요 (`frontend/src/lib/mapbox.ts`)

---

## 2. 백엔드 아키텍처 분석

### 2.1 디렉토리 구조 평가

**✅ 강점**:

```
backend/src/
├── api/v1/          # API 버전 관리 (좋은 관행)
├── core/            # 공유 로직 분리
├── config/          # 설정 중앙화
├── models/          # 데이터 모델
├── schemas/         # Pydantic 스키마 (요청/응답)
├── services/        # 비즈니스 로직 분리
└── integrations/    # 외부 API 통합
```

**장점**:
- 명확한 레이어 분리 (API → Services → Models)
- 관심사 분리 (Separation of Concerns) 준수
- 확장 가능한 구조

### 2.2 보안 아키텍처

**구현된 보안 기능** (`backend/src/core/security.py`):
- ✅ JWT 토큰 기반 인증
- ✅ Bcrypt 비밀번호 해싱
- ✅ HTTPBearer 보안 스키마

**개선 권장사항**:

#### 1. Rate Limiting 미구현 (T127 대기 중)

```python
# 권장: slowapi 또는 fastapi-limiter 추가
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/auth/login")
@limiter.limit("5/minute")  # 분당 5회 제한
async def login(...):
    ...
```

#### 2. CORS 설정 검토 필요 (`backend/src/main.py:35`)

```python
# 현재: allow_origins=settings.ALLOWED_ORIGINS
# 권장: 프로덕션에서 와일드카드(*) 사용 금지 확인
```

#### 3. 입력 검증 강화

- Pydantic 스키마 활용 중 (양호)
- SQL Injection 방어: SQLAlchemy ORM 사용으로 자동 방어됨 ✅

### 2.3 데이터 모델 설계

**ERD 품질**: ✅ **우수**

9개 핵심 엔티티의 관계 설계가 정규화되어 있음:
- User (1) → (M) TravelPlan
- TravelPlan (1) → (M) DailyItinerary
- DailyItinerary (1) → (M) ItineraryPlace → (1) Place

**강점**:
- 정규화된 스키마 (3NF 준수)
- 적절한 인덱스 전략 (외래 키, 자주 조회되는 필드)
- GIS 인덱스 계획 (위치 기반 검색)

**개선 제안**:

#### 1. 계산된 필드 중복

```python
# TravelPlan 모델
total_days = Column(Integer, NOT NULL)     # 계산됨
total_nights = Column(Integer, NOT NULL)   # 계산됨

# 권장: 데이터베이스에 저장 대신 property로 계산
@property
def total_days(self) -> int:
    return (self.end_date - self.start_date).days + 1
```

#### 2. 부족한 제약조건

```sql
-- 권장 추가:
ALTER TABLE users ADD CONSTRAINT check_email_format
  CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE places ADD CONSTRAINT check_rating_range
  CHECK (rating >= 0.0 AND rating <= 5.0);
```

---

## 3. 프론트엔드 아키텍처 분석

### 3.1 디렉토리 구조

**✅ 잘 구조화됨**:

```
frontend/src/
├── app/
│   ├── (auth)/          # 인증 필요 라우트 그룹
│   ├── (public)/        # 공개 라우트 (로그인/회원가입)
│   └── layout.tsx       # 루트 레이아웃
├── components/          # 재사용 가능 컴포넌트
├── hooks/               # 커스텀 훅 (useAuth)
└── lib/                 # 유틸리티 (api, supabase, mapbox)
```

**장점**:
- Next.js 15 App Router 활용 (라우트 그룹)
- 명확한 인증/공개 영역 분리

### 3.2 API 클라이언트 설계

**구현 품질**: ✅ **우수** (`frontend/src/lib/api.ts`)

**강점**:
- Axios Interceptor로 자동 토큰 주입
- 401 에러 시 자동 토큰 갱신 로직
- 에러 핸들링 타입 정의

**개선 제안**:

#### 1. 토큰 갱신 무한 루프 방지

```typescript
// 현재 코드의 잠재적 문제
if (error.response?.status === 401 && !originalRequest._retry) {
    originalRequest._retry = true
    // ...
}

// 권장: 재시도 횟수 제한 추가
const MAX_RETRIES = 1
if (!originalRequest._retryCount) {
    originalRequest._retryCount = 0
}
if (originalRequest._retryCount < MAX_RETRIES) {
    originalRequest._retryCount++
    // ... 토큰 갱신 로직
}
```

#### 2. 타임아웃 설정

```typescript
// 현재: timeout: 30000 (30초) ✅
// 권장: API별로 다른 타임아웃 설정 가능하게
export const longApiClient = axios.create({
    ...apiClient.defaults,
    timeout: 60000, // AI 생성용
})
```

---

## 4. 보안 및 인증 플로우

### 4.1 인증 아키텍처

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │         │   Backend   │         │  Supabase   │
│   (Next.js) │         │  (FastAPI)  │         │   (Auth)    │
└─────────────┘         └─────────────┘         └─────────────┘
      │                        │                        │
      │  1. 회원가입 요청      │                        │
      ├───────────────────────>│                        │
      │                        │  2. 사용자 생성         │
      │                        ├───────────────────────>│
      │                        │  3. JWT 발급            │
      │                        │<───────────────────────┤
      │  4. JWT 반환           │                        │
      │<───────────────────────┤                        │
      │                        │                        │
      │  5. API 요청 (JWT)     │                        │
      ├───────────────────────>│                        │
      │                        │  6. JWT 검증           │
      │                        ├───────────────────────>│
      │                        │  7. 검증 결과          │
      │                        │<───────────────────────┤
      │  8. 응답               │                        │
      │<───────────────────────┤                        │
```

**✅ 잘 구현된 부분**:
- Supabase Auth 통합
- JWT 토큰 기반 인증
- 자동 토큰 갱신 로직

**⚠️ 개선 필요**:

#### 1. 토큰 저장 위치

```typescript
// 현재: Supabase 클라이언트가 localStorage 사용 (기본값)
// 권장: XSS 공격 방지를 위해 httpOnly 쿠키 사용 고려

// 백엔드에서 쿠키 설정:
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,      # HTTPS only
    samesite="lax"
)
```

#### 2. CSRF 보호 (쿠키 사용 시)

```python
# 권장: fastapi-csrf-protect 또는 유사 라이브러리
from fastapi_csrf_protect import CsrfProtect
```

---

## 5. 확장성 및 성능

### 5.1 데이터베이스 확장성

**현재 설계**: ✅ 확장 가능

**강점**:
- 정규화된 스키마 (조인 비용 최적화 필요 시)
- 인덱스 전략 계획됨
- Alembic 마이그레이션 프레임워크

**성능 최적화 권장사항**:

#### 1. 데이터베이스 연결 풀링

```python
# 권장 추가:
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # 연결 풀 크기
    max_overflow=10,       # 추가 연결 허용
    pool_pre_ping=True,    # 연결 상태 확인
    pool_recycle=3600,     # 1시간마다 연결 재생성
)
```

#### 2. 읽기 전용 쿼리 최적화

```python
# 읽기 전용 트랜잭션 사용
@app.get("/v1/travel-plans/{plan_id}")
async def get_plan(plan_id: UUID, db: AsyncSession = Depends(get_db)):
    async with db.begin_nested():  # 읽기 전용
        plan = await db.get(TravelPlan, plan_id)
```

#### 3. N+1 쿼리 문제 방지

```python
# 권장: selectinload 또는 joinedload 사용
from sqlalchemy.orm import selectinload

stmt = select(TravelPlan).options(
    selectinload(TravelPlan.daily_itineraries)
    .selectinload(DailyItinerary.places)
)
```

### 5.2 캐싱 전략

**계획된 캐싱** (T123):
- Redis 캐싱 설정 (장소 데이터, 항공편 가격)

**권장 캐싱 레이어**:

```python
# 1. 애플리케이션 레벨 캐싱
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_popular_places(city: str):
    # 인기 장소 조회

# 2. Redis 캐싱 (외부 API 응답)
import aioredis

async def get_place_details(place_id: str):
    cache_key = f"place:{place_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # API 호출
    data = await google_maps.get_place(place_id)
    await redis.setex(cache_key, 86400, json.dumps(data))  # 24시간 TTL
    return data
```

---

## 6. 코드 품질 및 개발 경험

### 6.1 린팅 및 타입 검사

**백엔드** (`backend/pyproject.toml`):
- ✅ Black (코드 포매팅)
- ✅ Ruff (린팅)
- ✅ MyPy (타입 검사)
- ✅ 엄격한 타입 검사 설정 (`disallow_untyped_defs = true`)

**프론트엔드** (`frontend/package.json`):
- ✅ ESLint (Next.js 설정)
- ✅ Prettier (포매팅)
- ✅ TypeScript (타입 검사)

**개선 제안**:

#### Pre-commit Hooks (T008 완료 확인 필요)

```yaml
# .pre-commit-config.yaml 권장
repos:
  - repo: local
    hooks:
      - id: black
        name: black
        entry: black
        language: system
        types: [python]
      - id: ruff
        name: ruff
        entry: ruff
        language: system
        types: [python]
      - id: prettier
        name: prettier
        entry: prettier --write
        language: node
        types: [typescript, tsx]
```

### 6.2 테스트 전략

**현재 상태**: ⚠️ **테스트 부족**

**계획된 테스트** (T137-T139):
- T137: 백엔드 통합 테스트 (선택사항)
- T138: 프론트엔드 E2E 테스트 (선택사항)

**권장 테스트 구조**:

```python
# backend/tests/unit/test_security.py
import pytest
from src.core.security import create_access_token, verify_token

def test_token_creation():
    token = create_access_token({"sub": "user-id"})
    assert token is not None
    payload = verify_token(token)
    assert payload["sub"] == "user-id"

# backend/tests/integration/test_auth_api.py
@pytest.mark.asyncio
async def test_signup_flow(client):
    response = await client.post("/v1/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
```

---

## 7. 의존성 관리 및 배포

### 7.1 패키지 관리

**백엔드**:
- ✅ `uv` (Python 패키지 매니저) - 빠르고 모던함
- ✅ `pyproject.toml` (PEP 517 준수)

**프론트엔드**:
- ⚠️ npm 사용 중 (package-lock.json 확인 필요)
- 권장: pnpm 또는 yarn으로 전환 (모노레포 대비)

### 7.2 환경 변수 관리

**보안 권장사항**:

```bash
# backend/.env.example (템플릿 존재 확인 필요 - T007)
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<CHANGE_ME>  # 프로덕션에서 반드시 변경
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=...

# 권장: 시크릿 관리 도구 사용
# - AWS Secrets Manager
# - HashiCorp Vault
# - Doppler
```

### 7.3 배포 준비도

**프로덕션 체크리스트** (T140-T144):

- [ ] T140: 환경 변수 검토
- [ ] T141: Vercel 배포 설정 (프론트엔드)
- [ ] T142: Railway/Render 배포 설정 (백엔드)
- [ ] T143: 데이터베이스 마이그레이션 프로덕션 실행
- [ ] T144: CI/CD 파이프라인 설정

**권장 배포 전략**:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up --service backend

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel --prod
```

---

## 8. 모바일 준비도

### 8.1 PWA 전략

**계획된 접근**:
- Phase 1: PWA (Progressive Web App)
- Phase 2: Capacitor (앱스토어 배포)

**PWA 구현 체크리스트**:

```typescript
// frontend/next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
})

module.exports = withPWA({
  // Next.js config
})
```

```json
// frontend/public/manifest.json
{
  "name": "TravelTailor",
  "short_name": "TravelTailor",
  "icons": [...],
  "theme_color": "#000000",
  "background_color": "#ffffff",
  "display": "standalone",
  "start_url": "/"
}
```

---

## 9. 문제점 및 위험 요소

### 9.1 높은 우선순위 (즉시 해결 필요)

#### 1. 데이터베이스 마이그레이션 미완료 (T013)

```bash
# 영향: User, UserPreference 테이블 생성 안됨
# 해결: alembic revision --autogenerate 실행

cd backend
alembic revision --autogenerate -m "Add users and preferences"
alembic upgrade head
```

#### 2. Rate Limiting 부재

- **영향**: DoS 공격에 취약
- **해결**: T127 우선 구현 필요

#### 3. 외부 API 키 하드코딩 위험

```python
# config/settings.py
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set")
```

### 9.2 중간 우선순위 (Phase 3 전 해결)

#### 1. 에러 모니터링 미설정 (T130-T132)

- Sentry, PostHog 미설치
- 프로덕션 에러 추적 불가

#### 2. 테스트 커버리지 0%

- 리그레션 위험 높음
- 최소한 핵심 API 엔드포인트 테스트 필요

#### 3. API 문서 부족

- OpenAPI 스펙 자동 생성됨 (FastAPI)
- 추가 예시 및 설명 필요

### 9.3 낮은 우선순위 (향후 개선)

#### 1. 계산된 필드 중복 (데이터 모델)

- 스토리지 낭비 (미미함)
- 데이터 불일치 가능성

#### 2. 번들 크기 최적화 부족

- T125 대기 중
- 모바일 데이터 사용량 고려

---

## 10. 권장 개선 로드맵

### Phase 2 완료 전 (즉시)

1. **✅ T013: 데이터베이스 마이그레이션 실행**
   ```bash
   cd backend && alembic revision --autogenerate -m "Add users and preferences"
   alembic upgrade head
   ```

2. **✅ 환경 변수 템플릿 검증**
   - 파일: `backend/.env.example`, `frontend/.env.local.example`
   - 필수 변수: `DATABASE_URL`, `JWT_SECRET_KEY`, `OPENAI_API_KEY`

3. **✅ CORS 설정 검토**
   - 파일: `backend/src/main.py`
   - 확인: `settings.ALLOWED_ORIGINS`가 와일드카드(*) 아닌지

### Phase 3 시작 전 (1주일 내)

1. **보안 강화**
   - Rate limiting 구현 (T127)
   - 입력 검증 강화 (T128)
   - 시크릿 관리 도구 도입

2. **모니터링 설정**
   - Sentry 설치 및 설정
   - 로깅 레벨 조정
   - 헬스 체크 엔드포인트 개선

3. **기본 테스트 작성**
   - 인증 API 통합 테스트
   - 프론트엔드 E2E (로그인 플로우)

### Phase 8 (최적화) 전

1. **성능 최적화**
   - Redis 캐싱 (T123)
   - 데이터베이스 인덱스 검증
   - N+1 쿼리 문제 해결

2. **배포 준비**
   - CI/CD 파이프라인 (T144)
   - 환경별 설정 분리
   - 롤백 전략 수립

3. **문서화**
   - API 문서 업데이트 (T133)
   - 배포 가이드 작성 (T136)
   - 트러블슈팅 가이드

---

## 11. 최종 평가

### 11.1 점수표

| 영역 | 점수 (1-5) | 평가 |
|------|-----------|------|
| **아키텍처 설계** | 4.5 | 명확한 레이어 분리, 확장 가능 |
| **코드 품질** | 4.0 | 린팅 도구 설정, 타입 안전성 우수 |
| **보안** | 3.5 | JWT 구현 양호, Rate Limiting 부재 |
| **성능 설계** | 3.5 | 인덱스 계획됨, 캐싱 미구현 |
| **테스트** | 1.5 | 테스트 프레임워크만 설정됨 |
| **문서화** | 4.5 | 상세한 설계 문서, API 문서 자동 생성 |
| **배포 준비도** | 2.5 | 계획 존재, 실행 안됨 |

**종합 점수**: **3.4 / 5.0** (Good)

### 11.2 강점

1. **✅ 견고한 아키텍처 기반**
   - 명확한 프론트-백 분리
   - 확장 가능한 디렉토리 구조
   - API 버전 관리 체계

2. **✅ 우수한 데이터 모델 설계**
   - 정규화된 스키마
   - 명확한 엔티티 관계
   - 인덱스 전략 계획

3. **✅ 모던한 기술 스택**
   - FastAPI (비동기 지원)
   - Next.js 15 (최신 웹 프레임워크)
   - TypeScript (타입 안전성)

4. **✅ 상세한 계획 및 문서**
   - 144개 세분화된 태스크
   - 명확한 의존성 정의
   - 사용자 스토리 매핑

### 11.3 개선 필요 영역

1. **⚠️ 보안 강화 필요**
   - Rate limiting 구현
   - CSRF 보호 (쿠키 사용 시)
   - 시크릿 관리 체계

2. **⚠️ 테스트 커버리지 부족**
   - 단위 테스트 0%
   - 통합 테스트 0%
   - E2E 테스트 0%

3. **⚠️ 모니터링 미설정**
   - 에러 트래킹 없음
   - 성능 메트릭 수집 없음
   - 로그 집계 체계 없음

### 11.4 위험 요소

| 위험 | 심각도 | 완화 방안 |
|------|--------|-----------|
| React 19 RC 버전 | 중간 | 안정화 버전 출시 시 업그레이드 |
| 테스트 부재 | 높음 | 핵심 플로우 최소 테스트 작성 |
| Rate Limiting 부재 | 높음 | T127 우선 구현 |
| 외부 API 의존성 | 중간 | Graceful degradation 구현 |
| 데이터베이스 마이그레이션 미완료 | 높음 | T013 즉시 완료 |

---

## 12. 결론 및 권장사항

### 12.1 전반적 평가

**AI TravelTailor 프로젝트는 견고한 아키텍처 기반 위에 구축되고 있으며, 대부분의 설계 결정이 모범 사례를 따르고 있습니다.**

**주요 강점**:
- 명확한 레이어 분리 및 관심사 분리
- 확장 가능하고 유지보수 가능한 구조
- 상세한 계획 및 문서화

**해결 필요 사항**:
- 보안 강화 (Rate Limiting, 시크릿 관리)
- 테스트 커버리지 확보
- 모니터링 및 로깅 체계 구축

### 12.2 단계별 액션 플랜

**즉시 실행 (이번 주)**:
```bash
1. T013 완료: 데이터베이스 마이그레이션 실행
2. 환경 변수 검증 및 템플릿 생성
3. CORS 설정 검토 및 수정
```

**단기 (Phase 3 전)**:
```bash
1. Rate limiting 구현
2. 핵심 API 통합 테스트 작성 (최소 인증 플로우)
3. Sentry 에러 모니터링 설정
```

**중기 (MVP 배포 전)**:
```bash
1. E2E 테스트 작성 (주요 사용자 플로우)
2. CI/CD 파이프라인 구축
3. 성능 테스트 및 최적화
```

### 12.3 최종 추천

**✅ 프로젝트를 계속 진행하되, 다음 Phase 이동 전 보안 및 테스트 강화를 권장합니다.**

현재 구조는 충분히 견고하며, 위에서 언급한 개선사항들을 점진적으로 해결하면서 개발을 진행하면 성공적인 MVP를 출시할 수 있을 것입니다.

---

## 참고 문서

- [프로젝트 명세서](../specs/001-ai-travel-planner/spec.md)
- [구현 계획](../specs/001-ai-travel-planner/plan.md)
- [데이터 모델](../specs/001-ai-travel-planner/data-model.md)
- [작업 목록](../specs/001-ai-travel-planner/tasks.md)

---

**보고서 작성 완료** | 작성일: 2025-10-20 | 분석자: Architecture Review Team
