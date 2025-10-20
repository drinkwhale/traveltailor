# AI TravelTailor Backend

FastAPI 기반 여행 계획 생성 백엔드 서비스

## 기술 스택

- Python 3.11+
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL (Supabase)
- LangChain + OpenAI GPT-4
- **uv** - 빠른 Python 패키지 관리자

## 설치 및 실행

### uv 설치 (권장)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 프로젝트 설정

```bash
# 가상환경 생성 및 의존성 설치
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv pip install -e .

# 개발 의존성 포함 설치
uv pip install -e ".[dev]"
```

### 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### 개발 서버 실행

```bash
# uv를 사용한 실행
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 또는 가상환경 활성화 후
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성
uv run alembic revision --autogenerate -m "migration message"

# 마이그레이션 적용
uv run alembic upgrade head

# 마이그레이션 롤백
uv run alembic downgrade -1
```

## 개발 도구

```bash
# 코드 포맷팅
uv run black src/

# 린팅
uv run ruff check src/

# 타입 체크
uv run mypy src/

# 테스트 실행
uv run pytest
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## uv 주요 명령어

```bash
# 패키지 추가
uv pip install package-name

# 패키지 제거
uv pip uninstall package-name

# 의존성 동기화 (pyproject.toml 기반)
uv pip sync

# 명령어 실행
uv run <command>
```
