# AI TripSmith Backend

FastAPI 기반 여행 계획 생성 백엔드 서비스

## 기술 스택

- Python 3.11+
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL (Supabase)
- LangChain + OpenAI GPT-4

## 설치 및 실행

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정

# 개발 서버 실행
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
