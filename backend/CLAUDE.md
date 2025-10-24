# Backend 개발 가이드라인

AI TravelTailor 백엔드 - FastAPI 기반 AI 여행 일정 생성 API 서버

최종 업데이트: 2025-10-23

## 모듈 개요
FastAPI + SQLAlchemy + LangChain을 활용한 RESTful API 서버로, AI 기반 여행 일정 생성, 인증, 외부 API 연동(Google Places, OpenAI, Skyscanner 등), PDF 생성, 캐싱, 모니터링 등을 담당합니다.

## 기술 스택
- **언어**: Python 3.11+
- **프레임워크**: FastAPI 0.115.0, Uvicorn 0.32.0
- **ORM**: SQLAlchemy 2.0.36 (비동기), Alembic 1.14.0
- **DB 드라이버**: asyncpg 0.30.0, psycopg2-binary 2.9.10
- **AI/ML**: LangChain 0.3.7, OpenAI 1.54.4, tiktoken 0.8.0
- **작업 큐**: Celery 5.4.0 with Redis 5.0.8
- **인증**: Supabase 2.9.0, python-jose 3.3.0, passlib 1.7.4
- **보안**: fastapi-csrf-protect 0.3.4, SlowAPI 0.1.9 (레이트 리미팅)
- **외부 API**: googlemaps 4.10.0, requests 2.32.3, httpx 0.27.2
- **PDF 생성**: PyPDF2 3.0.1, Playwright 1.48.0
- **템플릿**: Jinja2 3.1.4
- **관측성**: Sentry 2.16.0, PostHog 3.5.0, Prometheus 0.21.0
- **테스트**: pytest 8.3.3, pytest-asyncio 0.24.0, pytest-cov 6.0.0
- **코드 품질**: black 24.10.0, ruff 0.7.4, mypy 1.13.0
- **패키지 관리**: uv

## 디렉토리 구조

```
backend/
├── src/
│   ├── api/                      # API 엔드포인트
│   │   ├── v1/                   # API v1 라우터
│   │   │   ├── auth.py          # 회원가입, 로그인, 로그아웃 (POST /v1/auth/signup, /v1/auth/login)
│   │   │   ├── trips.py         # 여행 일정 CRUD (GET/POST/PUT/DELETE /v1/trips)
│   │   │   ├── places.py        # 장소 검색 및 상세 (GET /v1/places/search, /v1/places/{id})
│   │   │   ├── accommodations.py # 숙소 검색 (GET /v1/accommodations/search)
│   │   │   ├── flights.py       # 항공편 검색 (GET /v1/flights/search)
│   │   │   ├── csrf.py          # CSRF 토큰 발급 (GET /v1/csrf-token)
│   │   │   └── pdf.py           # PDF 생성 (POST /v1/trips/{id}/pdf)
│   │   ├── dependencies.py      # FastAPI 의존성 (get_db, get_current_user 등)
│   │   └── __init__.py
│   │
│   ├── config/                   # 환경 설정
│   │   ├── settings.py          # Pydantic Settings (환경 변수 관리)
│   │   ├── database.py          # SQLAlchemy 엔진, 세션 팩토리
│   │   ├── redis.py             # Redis 클라이언트 설정
│   │   └── celery_config.py     # Celery 작업 큐 설정
│   │
│   ├── core/                     # 핵심 비즈니스 로직
│   │   ├── travel_planner.py    # AI 여행 일정 생성 오케스트레이터
│   │   ├── ai_agent.py          # LangChain 에이전트 (GPT-4o 기반)
│   │   ├── route_optimizer.py   # 경로 최적화 알고리즘 (TSP)
│   │   ├── budget_calculator.py # 예산 계산 로직
│   │   ├── preference_matcher.py # 사용자 선호도 매칭
│   │   └── itinerary_builder.py # 일정표 구조 생성
│   │
│   ├── integrations/             # 외부 API 연동
│   │   ├── openai_integration.py    # OpenAI API (LangChain 래퍼)
│   │   ├── google_places_integration.py # Google Places API
│   │   ├── skyscanner_integration.py    # Skyscanner API (항공편)
│   │   ├── booking_integration.py       # Booking.com Affiliate (숙소)
│   │   ├── agoda_integration.py         # Agoda API (숙소)
│   │   └── mapbox_integration.py        # Mapbox Directions API
│   │
│   ├── metrics/                  # Prometheus 메트릭
│   │   ├── prometheus.py        # 메트릭 정의 및 수집
│   │   └── __init__.py
│   │
│   ├── middleware/               # 미들웨어
│   │   ├── cors.py              # CORS 설정
│   │   ├── error_handler.py     # 전역 예외 처리
│   │   ├── rate_limit.py        # SlowAPI 레이트 리미팅
│   │   ├── security.py          # CSRF, XSS 방어, 보안 헤더
│   │   └── logging.py           # 요청/응답 로깅
│   │
│   ├── models/                   # SQLAlchemy 모델
│   │   ├── user.py              # User 모델 (인증 정보)
│   │   ├── trip.py              # Trip 모델 (여행 일정 메타데이터)
│   │   ├── place.py             # Place 모델 (장소 정보, PostGIS 좌표)
│   │   ├── accommodation.py     # Accommodation 모델 (숙소 정보)
│   │   ├── itinerary_item.py    # ItineraryItem 모델 (일정 항목)
│   │   ├── preference.py        # UserPreference 모델 (사용자 선호도)
│   │   └── __init__.py
│   │
│   ├── schemas/                  # Pydantic 스키마
│   │   ├── auth.py              # 인증 요청/응답 스키마
│   │   ├── trip.py              # 여행 일정 요청/응답 스키마
│   │   ├── place.py             # 장소 요청/응답 스키마
│   │   ├── accommodation.py     # 숙소 요청/응답 스키마
│   │   ├── flight.py            # 항공편 요청/응답 스키마
│   │   ├── user.py              # 사용자 스키마
│   │   └── __init__.py
│   │
│   ├── services/                 # 서비스 레이어 (비즈니스 로직)
│   │   ├── auth_service.py      # 인증 서비스 (회원가입, 로그인, JWT 발급)
│   │   ├── trip_service.py      # 여행 일정 서비스 (생성, 조회, 수정, 삭제)
│   │   ├── place_service.py     # 장소 서비스 (검색, 상세 정보)
│   │   ├── accommodation_service.py # 숙소 서비스
│   │   ├── flight_service.py    # 항공편 서비스
│   │   ├── pdf/                 # PDF 생성 서비스
│   │   │   ├── generator.py     # Playwright 기반 HTML-to-PDF
│   │   │   └── templates/       # Jinja2 템플릿
│   │   └── __init__.py
│   │
│   ├── utils/                    # 유틸리티
│   │   ├── logger.py            # 구조화된 로깅 (JSON)
│   │   ├── security.py          # 비밀번호 해싱, 토큰 검증
│   │   ├── validators.py        # 입력 검증 헬퍼
│   │   └── __init__.py
│   │
│   └── main.py                   # FastAPI 애플리케이션 진입점
│
├── alembic/                      # DB 마이그레이션
│   ├── versions/                # 마이그레이션 히스토리
│   ├── env.py                   # Alembic 환경 설정
│   └── alembic.ini              # Alembic 설정 파일
│
├── tests/                        # pytest 테스트
│   ├── conftest.py              # pytest fixture
│   ├── test_auth.py             # 인증 API 테스트
│   ├── test_trips.py            # 여행 일정 API 테스트
│   ├── test_places.py           # 장소 API 테스트
│   └── ...
│
├── pyproject.toml                # Python 의존성 및 도구 설정
├── .env.example                  # 환경 변수 템플릿
└── README.md                     # 백엔드 실행 가이드
```

## 핵심 파일 설명

### 진입점 및 설정
- **[src/main.py](src/main.py:1)**: FastAPI 앱 초기화, 미들웨어 등록, 라우터 포함, Sentry/PostHog 초기화, Prometheus `/metrics` 노출
- **[src/config/settings.py](src/config/settings.py:1)**: Pydantic Settings로 환경 변수 관리 (DB URL, API 키, JWT 설정 등)
- **[src/config/database.py](src/config/database.py:1)**: SQLAlchemy 비동기 엔진 및 세션 팩토리 (asyncpg 드라이버)

### 핵심 비즈니스 로직
- **[src/core/travel_planner.py](src/core/travel_planner.py:1)**: AI 여행 일정 생성 오케스트레이터. LangChain 에이전트 호출, 장소 검색, 경로 최적화, 예산 계산을 통합
- **[src/core/ai_agent.py](src/core/ai_agent.py:1)**: LangChain + OpenAI GPT-4o 에이전트. 프롬프트 템플릿 관리, 토큰 제한 검증
- **[src/core/route_optimizer.py](src/core/route_optimizer.py:1)**: TSP(Traveling Salesman Problem) 알고리즘으로 장소 간 최적 경로 계산

### API 엔드포인트
- **[src/api/v1/auth.py](src/api/v1/auth.py:1)**: `POST /v1/auth/signup`, `POST /v1/auth/login`, `POST /v1/auth/logout`
- **[src/api/v1/trips.py](src/api/v1/trips.py:1)**: `GET /v1/trips`, `POST /v1/trips`, `GET /v1/trips/{id}`, `PUT /v1/trips/{id}`, `DELETE /v1/trips/{id}`
- **[src/api/v1/places.py](src/api/v1/places.py:1)**: `GET /v1/places/search?query={query}&location={lat,lng}`, `GET /v1/places/{id}`
- **[src/api/v1/pdf.py](src/api/v1/pdf.py:1)**: `POST /v1/trips/{id}/pdf` (Playwright 기반 PDF 생성)

### 외부 API 연동
- **[src/integrations/openai_integration.py](src/integrations/openai_integration.py:1)**: OpenAI API 클라이언트, LangChain 래퍼, 토큰 사용량 추적
- **[src/integrations/google_places_integration.py](src/integrations/google_places_integration.py:1)**: Google Places API 클라이언트, Redis 캐싱 (15분 TTL)
- **[src/integrations/skyscanner_integration.py](src/integrations/skyscanner_integration.py:1)**: Skyscanner API 클라이언트, 항공편 검색, 가격 비교

### 서비스 레이어
- **[src/services/auth_service.py](src/services/auth_service.py:1)**: 회원가입, 로그인, JWT 토큰 발급/검증, 비밀번호 해싱
- **[src/services/trip_service.py](src/services/trip_service.py:1)**: 여행 일정 CRUD, AI 생성 요청 처리, Fallback 템플릿 반환
- **[src/services/pdf/generator.py](src/services/pdf/generator.py:1)**: Playwright로 HTML 렌더링 후 PDF 변환, Jinja2 템플릿 사용

### 미들웨어 및 보안
- **[src/middleware/rate_limit.py](src/middleware/rate_limit.py:15)**: SlowAPI 레이트 리미팅 (로그인/회원가입 5회/분, 그 외 100회/분)
- **[src/middleware/security.py](src/middleware/security.py:1)**: CSRF 보호, XSS 방어, 보안 헤더 (`X-Content-Type-Options`, `X-Frame-Options` 등)
- **[src/middleware/error_handler.py](src/middleware/error_handler.py:1)**: 전역 예외 처리, Sentry 에러 리포팅

### 모델
- **[src/models/trip.py](src/models/trip.py:1)**: Trip 모델 (user_id, destination, start_date, end_date, budget, preferences JSONB)
- **[src/models/place.py](src/models/place.py:18)**: Place 모델 (name, coordinates GEOGRAPHY(POINT), PostGIS GIST 인덱스)
- **[src/models/user.py](src/models/user.py:1)**: User 모델 (email, hashed_password, is_verified)

## 주요 명령어

### 개발 환경 설정
```bash
cd backend
uv venv                           # 가상환경 생성
source .venv/bin/activate         # 가상환경 활성화 (Windows: .venv\Scripts\activate)
uv pip install -e ".[dev]"        # 의존성 설치 (개발 도구 포함)
```

### 환경 변수 설정
```bash
cp .env.example .env
# 필수 환경 변수 설정:
# - DATABASE_URL: PostgreSQL 연결 문자열 (Supabase)
# - SUPABASE_URL, SUPABASE_KEY: Supabase 프로젝트 정보
# - OPENAI_API_KEY: OpenAI API 키
# - JWT_SECRET_KEY: JWT 토큰 서명 키
# - GOOGLE_PLACES_API_KEY: Google Places API 키
# - REDIS_URL: Redis 연결 문자열 (캐싱용)
```

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 파일 자동 생성
uv run alembic revision --autogenerate -m "Add user preferences table"

# 마이그레이션 적용
uv run alembic upgrade head

# 마이그레이션 롤백
uv run alembic downgrade -1
```

### 서버 실행
```bash
# 개발 서버 (핫 리로드 활성화)
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버 (Gunicorn + Uvicorn workers)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 테스트 및 코드 품질
```bash
# 전체 테스트 실행 (커버리지 포함)
uv run pytest

# 특정 테스트 파일 실행
uv run pytest tests/test_auth.py -v

# 특정 테스트 함수 실행
uv run pytest tests/test_auth.py::test_login_success -v

# 코드 포맷팅 (Black)
uv run black src/ tests/

# Linting (Ruff)
uv run ruff check src/ tests/
uv run ruff check --fix src/ tests/  # 자동 수정

# 타입 체킹 (mypy)
uv run mypy src/
```

### Celery 작업 큐 (백그라운드 작업)
```bash
# Celery worker 실행
celery -A src.config.celery_config worker --loglevel=info

# Celery beat 실행 (스케줄링)
celery -A src.config.celery_config beat --loglevel=info
```

## 코드 스타일 및 규칙

### 포맷팅
- **Black**: line-length=100, target-version=py311
- 모든 커밋 전 `uv run black src/ tests/` 실행

### Linting
- **Ruff**: pycodestyle, pyflakes, isort, flake8-bugbear, flake8-comprehensions
- E501 (line too long) 무시 (Black이 처리)
- 모든 PR 전 `uv run ruff check --fix src/ tests/` 실행

### 타입 힌팅
- **mypy**: strict mode (disallow_untyped_defs, check_untyped_defs)
- 모든 함수에 타입 힌트 필수 (매개변수, 반환값)
- 외부 라이브러리(langchain, googlemaps 등)는 `ignore_missing_imports = true`

### 네이밍 컨벤션
- **함수/변수**: snake_case (예: `get_current_user`, `trip_service`)
- **클래스**: PascalCase (예: `TripService`, `UserModel`)
- **상수**: UPPER_SNAKE_CASE (예: `JWT_SECRET_KEY`, `REDIS_TTL`)
- **비공개 함수**: _로 시작 (예: `_validate_token`)

## 중요 규칙 및 제약사항

### 데이터베이스
1. **비동기 ORM**: SQLAlchemy의 `asyncio` 확장 사용. 모든 DB 쿼리는 `await` 필요
   ```python
   async with get_db() as db:
       result = await db.execute(select(User).where(User.id == user_id))
       user = result.scalar_one_or_none()
   ```

2. **마이그레이션**: DB 스키마 변경 시 반드시 Alembic 사용. 수동 SQL 실행 금지
   ```bash
   uv run alembic revision --autogenerate -m "description"
   uv run alembic upgrade head
   ```

3. **공간 인덱스**: Place 모델의 `coordinates` 필드는 PostGIS `GEOGRAPHY(POINT)` 타입 사용. GIST 인덱스로 근접 검색 최적화
   ```python
   coordinates = Column(Geography(geometry_type='POINT', srid=4326), nullable=False, index=True)
   ```

4. **트랜잭션**: 복수 테이블 수정 시 트랜잭션 사용
   ```python
   async with db.begin():
       db.add(trip)
       db.add(itinerary_item)
       await db.commit()
   ```

### 외부 API 연동
1. **레이트 리미팅**: 모든 외부 API 호출에 재시도 로직 (tenacity 라이브러리)
   ```python
   @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
   async def call_google_places_api(query: str) -> dict:
       ...
   ```

2. **캐싱**: Redis 캐시 우선 조회, 미스 시 API 호출 후 캐싱
   - Google Places: 15분 TTL
   - 항공편 검색: 5분 TTL
   - 장소 상세 정보: 1시간 TTL

3. **API 키 관리**: 환경 변수에서만 로드, 하드코딩 금지. `settings.py`에서 검증
   ```python
   OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
   ```

### AI/ML
1. **프롬프트 템플릿**: [src/core/ai_agent.py:45](src/core/ai_agent.py#L45)에서 중앙 관리. 프롬프트 변경 시 반드시 이 파일 수정
   ```python
   TRAVEL_PLANNER_PROMPT = PromptTemplate(
       input_variables=["destination", "budget", "preferences"],
       template="..."
   )
   ```

2. **토큰 제한**: OpenAI API 요청당 최대 4096 토큰. tiktoken으로 사전 검증
   ```python
   import tiktoken
   encoding = tiktoken.encoding_for_model("gpt-4o")
   token_count = len(encoding.encode(prompt_text))
   if token_count > 4096:
       raise ValueError("Prompt exceeds token limit")
   ```

3. **Fallback**: AI 생성 실패 시 캐시된 템플릿 일정 반환 ([src/services/trip_service.py:123](src/services/trip_service.py#L123))
   ```python
   try:
       itinerary = await ai_agent.generate_itinerary(request)
   except Exception as e:
       logger.error(f"AI generation failed: {e}")
       itinerary = load_fallback_template(request.destination)
   ```

### 보안
1. **CSRF 보호**: 모든 상태 변경 요청(POST/PUT/DELETE)에 `X-CSRF-Token` 헤더 필수
   - [src/middleware/security.py](src/middleware/security.py:1)에서 검증
   - `GET /v1/csrf-token`에서 토큰 발급

2. **레이트 리미팅**: SlowAPI로 엔드포인트별 요청 제한
   - 로그인/회원가입: 5회/분
   - 그 외 엔드포인트: 100회/분 (글로벌)
   - [src/middleware/rate_limit.py:15](src/middleware/rate_limit.py#L15)

3. **비밀번호 해싱**: passlib의 bcrypt 사용. 평문 저장 절대 금지
   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   hashed_password = pwd_context.hash(plain_password)
   ```

4. **환경 변수 검증**: `.env` 파일을 절대 커밋하지 말 것. `.gitignore`에 `.env` 포함 확인

### 에러 처리
1. **구조화된 예외**: 커스텀 예외 클래스 사용 (HTTPException 래퍼)
   ```python
   class TripNotFoundException(HTTPException):
       def __init__(self, trip_id: int):
           super().__init__(status_code=404, detail=f"Trip {trip_id} not found")
   ```

2. **Sentry 리포팅**: 모든 500 에러는 자동으로 Sentry에 리포팅. [src/main.py](src/main.py:1)에서 초기화
   ```python
   sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.APP_ENV)
   ```

3. **로깅**: 구조화된 JSON 로깅 ([src/utils/logger.py](src/utils/logger.py:1))
   ```python
   logger.info("User logged in", extra={"user_id": user.id, "email": user.email})
   ```

### 테스트
1. **Fixture**: `conftest.py`에 공통 fixture 정의 (test DB, mock 외부 API)
2. **DB 격리**: 각 테스트는 독립된 트랜잭션에서 실행, 롤백 처리
3. **Mock 외부 API**: `pytest-mock`으로 외부 API 호출 모킹 (실제 API 호출 금지)
4. **커버리지 목표**: 80% 이상 (pytest-cov로 측정)

## 모니터링 및 관측성

### Prometheus 메트릭
- **엔드포인트**: `GET /metrics`
- **메트릭 종류**:
  - `http_requests_total`: HTTP 요청 수 (상태 코드별)
  - `http_request_duration_seconds`: 요청 처리 시간
  - `ai_generation_duration_seconds`: AI 일정 생성 시간
  - `external_api_calls_total`: 외부 API 호출 수 (서비스별)
- **정의**: [src/metrics/prometheus.py](src/metrics/prometheus.py:1)

### Sentry
- **DSN**: `SENTRY_DSN` 환경 변수 설정
- **에러 리포팅**: 500 에러 자동 캡처, 사용자 컨텍스트 포함
- **성능 추적**: 트랜잭션 추적 (AI 생성, DB 쿼리, 외부 API 호출)

### PostHog
- **API Key**: `POSTHOG_API_KEY` 환경 변수 설정
- **이벤트**: 사용자 행동 추적 (여행 생성, PDF 다운로드 등)
- **개인정보 마스킹**: 이메일, IP 주소 자동 마스킹

## 배포
- **Dockerfile**: 멀티스테이지 빌드 (uv로 의존성 설치)
- **헬스체크**: `GET /health` (DB 연결, Redis 연결 확인)
- **CI/CD**: GitHub Actions (pytest, ruff, black, mypy, Docker 빌드/푸시)
- **환경 변수**: GitHub Secrets 또는 AWS Secrets Manager 사용

## 문제 해결

### 자주 발생하는 오류

1. **ImportError: cannot import name 'X' from 'Y'**
   - 해결: `uv pip install -e ".[dev]"` 재실행

2. **sqlalchemy.exc.OperationalError: could not connect to server**
   - 해결: `.env`의 `DATABASE_URL` 확인, PostgreSQL 실행 확인

3. **OpenAI API rate limit exceeded**
   - 해결: 레이트 리미팅 재시도 로직 확인, API 키 쿼터 확인

4. **Alembic migration conflict**
   - 해결: `alembic downgrade -1` 후 충돌 해결, 다시 `alembic upgrade head`

## 추가 리소스
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 비동기 문서](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [LangChain 문서](https://python.langchain.com/docs/get_started/introduction)
- [Alembic 마이그레이션 가이드](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostGIS 공간 인덱스 문서](https://postgis.net/docs/using_postgis_dbmanagement.html#spatial_indexes)
