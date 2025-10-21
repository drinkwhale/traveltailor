# AI TravelTailor Backend

AI가 개인 맞춤형 여행 일정을 생성할 수 있도록 하는 FastAPI 기반 백엔드입니다. 인증, 일정 생성, 외부 데이터 수집, PDF/지도용 데이터 공급을 담당합니다.

## 주요 구성 요소
- **FastAPI + Uvicorn**: REST API 및 OpenAPI 문서 제공
- **SQLAlchemy + Alembic**: Supabase(PostgreSQL)와의 데이터 영속화
- **LangChain + OpenAI GPT-4o**: 여행 일정 생성 파이프라인 (폴백/타임아웃 로직 포함)
- **외부 연동**: Google Places, Mapbox, 항공/숙박 추천 API
- **품질 도구**: `ruff`, `black`, `mypy`, `pytest`

## 사전 준비물
- Python 3.11 이상
- [uv](https://github.com/astral-sh/uv) (권장) 또는 표준 `pip`
- Supabase 프로젝트 (PostgreSQL / Auth)
- OpenAI, Google Maps, Mapbox, Skyscanner 등 외부 API 키

## 환경 변수
환경 변수 템플릿은 `.env.example`에 정리돼 있습니다. 필수 키는 아래와 같습니다.

| 영역 | 키 |
| --- | --- |
| 앱/보안 | `APP_ENV`, `SECRET_KEY`, `JWT_SECRET_KEY` |
| DB/Supabase | `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY` |
| AI | `OPENAI_API_KEY` |
| 외부 API | `GOOGLE_MAPS_API_KEY`, `MAPBOX_ACCESS_TOKEN`, `SKYSCANNER_API_KEY` |

```bash
cp .env.example .env
```

Supabase 연결 정보와 API 키를 채운 뒤 실행하세요.

## 설치 및 개발 서버 실행

```bash
# uv가 설치되어 있지 않다면 먼저 설치하세요
# macOS/Linux
#   curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
#   irm https://astral.sh/uv/install.ps1 | iex

# 가상환경 생성 및 의존성 설치
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# 개발 서버 (자동 리로드)
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

`uv`를 사용할 수 없는 환경이라면 `python -m venv`와 `pip install -e ".[dev]"`를 그대로 사용하면 됩니다.

## 데이터베이스 마이그레이션

```bash
# 최신 마이그레이션 적용
uv run alembic upgrade head

# 새 마이그레이션 생성
uv run alembic revision --autogenerate -m "add travel plan tables"

# 롤백
uv run alembic downgrade -1
```

새로운 테이블/컬럼을 추가할 때는 **마이그레이션 작성 → 테스트 데이터베이스에서 드라이런** 순서를 지켜주세요. (`specs/001-ai-travel-planner/tasks.md`의 T013/T013a 참고)

## 품질 점검

```bash
uv run ruff check src/ tests/
uv run black src/ tests/
uv run mypy src/
uv run pytest
```

CI에 적용 예정인 규칙과 동일하므로 변경 사항을 커밋하기 전에 실행하는 것을 권장합니다.

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 추가 자료
- 전체 기능/요구사항: `specs/001-ai-travel-planner/spec.md`
- 구현 계획: `specs/001-ai-travel-planner/plan.md`
- 작업 목록 및 체크포인트: `specs/001-ai-travel-planner/tasks.md`
