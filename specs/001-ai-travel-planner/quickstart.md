# 개발자 빠른 시작 가이드: AI TripSmith

**최종 업데이트**: 2025-10-19
**대상 독자**: 처음으로 프로젝트를 설정하는 개발자

## 개요

AI TripSmith는 AI를 사용하여 개인화된 여행 일정을 생성하는 웹 애플리케이션입니다. 이 가이드는 개발 환경을 설정하고 프로젝트 구조를 이해하는 데 도움을 줍니다.

---

## 사전 요구사항

### 필수 소프트웨어

- **Node.js**: v20.11+ (프론트엔드 및 PDF 생성용)
- **Python**: 3.11+ (백엔드 AI 서비스용)
- **PostgreSQL**: 15+ (Supabase 또는 로컬)
- **Git**: 버전 관리용
- **Docker** (선택사항): 컨테이너화된 개발용

### 권장 도구

- **VS Code** 및 확장 프로그램:
  - Python
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
- **Postman** 또는 **Bruno**: API 테스트용
- **TablePlus** 또는 **pgAdmin**: 데이터베이스 검사용

---

## 빠른 설정

### 1. 저장소 복제

```bash
git clone <repository-url>
cd traveltailor
```

### 2. 환경 설정

프론트엔드와 백엔드 모두에 대한 환경 파일 생성:

**백엔드: `backend/.env`**
```env
# 데이터베이스 (Supabase)
DATABASE_URL=postgresql://user:password@host:5432/tripsmith
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# AI 서비스
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# 외부 API
GOOGLE_PLACES_API_KEY=...
SKYSCANNER_API_KEY=...
BOOKING_AFFILIATE_ID=...
AGODA_API_KEY=...
MAPBOX_ACCESS_TOKEN=...

# 인증
JWT_SECRET_KEY=<generate-random-string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# 애플리케이션
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000

# PDF 생성
PDF_TEMP_DIR=/tmp/tripsmith-pdfs
```

**프론트엔드: `frontend/.env.local`**
```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/v1

# Supabase (클라이언트 측 인증용)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# 지도
NEXT_PUBLIC_MAPBOX_TOKEN=...

# 분석 (개발 시 선택사항)
NEXT_PUBLIC_POSTHOG_KEY=...
NEXT_PUBLIC_SENTRY_DSN=...
```

### 3. 백엔드 설정

```bash
cd backend

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션 실행
alembic upgrade head

# 데이터베이스 시드 (선택사항)
python scripts/seed_data.py

# 개발 서버 시작
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

백엔드 접속 주소: `http://localhost:8000`
API 문서 (Swagger UI): `http://localhost:8000/docs`

### 4. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install
# 또는
pnpm install

# 개발 서버 실행
npm run dev
# 또는
pnpm dev
```

프론트엔드 접속 주소: `http://localhost:3000`

---

## 프로젝트 구조

### 백엔드 (`backend/`)

```
backend/
├── src/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── config.py               # 설정 및 환경 변수
│   │
│   ├── models/                 # SQLAlchemy ORM 모델
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── travel_plan.py
│   │   ├── place.py
│   │   └── ...
│   │
│   ├── schemas/                # 요청/응답용 Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── travel_plan.py
│   │   └── ...
│   │
│   ├── api/                    # API 라우트
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # 인증 엔드포인트
│   │   │   ├── travel_plans.py # 여행 계획 CRUD
│   │   │   ├── places.py       # 장소 검색
│   │   │   ├── exports.py      # PDF 및 지도 내보내기
│   │   │   └── recommendations.py
│   │   └── dependencies.py     # 공유 의존성 (인증, DB)
│   │
│   ├── services/               # 비즈니스 로직
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── planner.py      # 핵심 AI 계획 로직
│   │   │   ├── prompts.py      # LangChain 프롬프트
│   │   │   └── memory.py       # 사용자 선호도 메모리
│   │   ├── places/
│   │   │   ├── __init__.py
│   │   │   └── search.py       # 장소 추천
│   │   ├── routes/
│   │   │   └── optimizer.py    # 경로 최적화
│   │   └── pdf/
│   │       ├── __init__.py
│   │       └── generator.py    # PDF 생성
│   │
│   ├── integrations/           # 외부 API 클라이언트
│   │   ├── google_maps.py
│   │   ├── skyscanner.py
│   │   ├── booking.py
│   │   └── ...
│   │
│   └── core/                   # 핵심 유틸리티
│       ├── database.py         # 데이터베이스 연결
│       ├── security.py         # JWT, 비밀번호 해싱
│       └── exceptions.py       # 커스텀 예외
│
├── tests/                      # 테스트 스위트
│   ├── conftest.py             # Pytest 픽스처
│   ├── unit/
│   ├── integration/
│   └── contract/
│
├── alembic/                    # 데이터베이스 마이그레이션
│   └── versions/
│
├── scripts/                    # 유틸리티 스크립트
│   └── seed_data.py
│
├── requirements.txt            # Python 의존성
├── requirements-dev.txt        # 개발 의존성
└── pytest.ini                  # Pytest 설정
```

### 프론트엔드 (`frontend/`)

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # 루트 레이아웃
│   │   ├── page.tsx            # 홈 페이지
│   │   │
│   │   ├── (auth)/             # 인증된 라우트 그룹
│   │   │   ├── create/         # 여행 계획 생성
│   │   │   │   └── page.tsx
│   │   │   ├── history/        # 계획 히스토리 보기
│   │   │   │   └── page.tsx
│   │   │   └── plan/[id]/      # 특정 계획 보기/수정
│   │   │       └── page.tsx
│   │   │
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   │
│   ├── components/             # React 컴포넌트
│   │   ├── forms/
│   │   │   ├── TravelPlanForm.tsx
│   │   │   └── PreferencesForm.tsx
│   │   ├── map/
│   │   │   ├── MapView.tsx
│   │   │   └── RouteMap.tsx
│   │   ├── timeline/
│   │   │   ├── DailyTimeline.tsx
│   │   │   └── PlaceCard.tsx
│   │   ├── ui/                 # Shadcn UI 컴포넌트
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   └── ...
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Footer.tsx
│   │
│   ├── services/               # API 클라이언트 서비스
│   │   ├── api.ts              # 기본 API 클라이언트 (Axios/Fetch)
│   │   ├── travel-plans.ts
│   │   ├── auth.ts
│   │   └── places.ts
│   │
│   ├── hooks/                  # 커스텀 React 훅
│   │   ├── useTravelPlan.ts
│   │   ├── useAuth.ts
│   │   └── useMap.ts
│   │
│   ├── lib/                    # 유틸리티 함수
│   │   ├── utils.ts
│   │   ├── supabase.ts         # Supabase 클라이언트
│   │   └── validators.ts
│   │
│   └── types/                  # TypeScript 타입
│       ├── api.ts
│       ├── models.ts
│       └── index.ts
│
├── public/                     # 정적 에셋
│   ├── images/
│   └── fonts/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/                    # Playwright 테스트
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## 주요 개발 워크플로우

### 1. 새 API 엔드포인트 생성

**백엔드**:

1. `src/schemas/`에 Pydantic 스키마 정의
2. `src/api/v1/`에 라우트 추가
3. `src/services/`에 서비스 로직 구현
4. `tests/`에 테스트 작성

예시:
```python
# src/api/v1/example.py
from fastapi import APIRouter, Depends
from src.schemas.example import ExampleRequest, ExampleResponse
from src.services.example import ExampleService

router = APIRouter()

@router.post("/example", response_model=ExampleResponse)
async def create_example(
    request: ExampleRequest,
    service: ExampleService = Depends()
):
    return await service.process(request)
```

**프론트엔드**:

1. `src/services/`에 API 클라이언트 함수 추가
2. 필요시 커스텀 훅 생성
3. 컴포넌트에서 사용

예시:
```typescript
// src/services/example.ts
export async function createExample(data: ExampleRequest) {
  return api.post('/example', data);
}

// src/hooks/useExample.ts
export function useExample() {
  return useMutation({
    mutationFn: createExample,
  });
}
```

### 2. 데이터베이스 모델 추가

1. `src/models/`에 SQLAlchemy 모델 생성
2. 마이그레이션 생성: `alembic revision --autogenerate -m "Add example table"`
3. `alembic/versions/`에서 마이그레이션 검토 및 수정
4. 마이그레이션 적용: `alembic upgrade head`

### 3. AI 프롬프트 테스트

대화형 Python REPL 사용:

```bash
cd backend
source venv/bin/activate
python

>>> from src.services.ai.planner import TravelPlanner
>>> planner = TravelPlanner()
>>> result = planner.generate_plan({
...     "destination": "Tokyo",
...     "start_date": "2025-11-01",
...     "end_date": "2025-11-04",
...     "budget_total": 800000,
...     "traveler_type": "couple",
...     "preferences": {"interests": ["food"]}
... })
>>> print(result)
```

---

## 일반 작업

### 테스트 실행

**백엔드**:
```bash
# 전체 테스트
pytest

# 특정 테스트 파일
pytest tests/unit/test_planner.py

# 커버리지 포함
pytest --cov=src --cov-report=html
```

**프론트엔드**:
```bash
# 유닛 테스트
npm test

# E2E 테스트
npm run test:e2e
```

### 데이터베이스 관리

```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 하나 롤백
alembic downgrade -1

# 마이그레이션 히스토리 보기
alembic history
```

### 코드 포맷팅

**백엔드**:
```bash
# black으로 포맷
black src/

# ruff로 린트
ruff check src/

# mypy로 타입 체크
mypy src/
```

**프론트엔드**:
```bash
# 포맷 및 린트
npm run lint
npm run format
```

---

## 환경별 주의사항

### 개발 환경
- 프론트엔드 및 백엔드 모두 핫 리로드 활성화
- 상세한 오류 메시지 및 스택 트레이스
- CORS가 localhost 출처 허용
- 자세한 로깅

### 테스트 환경
- 별도의 테스트 데이터베이스 사용
- 외부 API 호출 모킹
- 이메일 발송 비활성화
- 테스트 API 키 사용

### 프로덕션 환경
- HTTPS만 활성화
- 적절한 CORS 출처 설정
- 프로덕션 데이터베이스 사용
- 에러 모니터링 활성화 (Sentry)
- 적절한 Rate Limit 설정

---

## 문제 해결

### 백엔드가 시작되지 않음

1. **Python 버전 확인**: `python --version` (3.11+ 이어야 함)
2. **가상 환경 확인**: `which python` (venv를 가리켜야 함)
3. **환경 변수 확인**: `.env` 파일 존재 여부
4. **데이터베이스 연결**: `psql $DATABASE_URL`로 테스트

### 프론트엔드 빌드 실패

1. **캐시 정리**: `rm -rf .next node_modules && npm install`
2. **Node 버전 확인**: `node --version` (20+ 이어야 함)
3. **환경 변수 확인**: `.env.local` 체크

### AI 생성이 느림

1. **OpenAI API 상태 확인**: https://status.openai.com
2. **API Rate Limit 확인**: OpenAI 대시보드 체크
3. **캐싱 활성화**: 장소 데이터 캐싱에 Redis 사용
4. **프롬프트 최적화**: 토큰 사용량 줄이기

### PDF 생성 실패

1. **Puppeteer 설치 확인**: `npm list puppeteer`
2. **시스템 폰트 확인**: 필요한 폰트 설치 여부
3. **임시 디렉토리 확인**: `PDF_TEMP_DIR`이 쓰기 가능한지 확인

---

## 유용한 명령어

### 개발

```bash
# 백엔드
cd backend && source venv/bin/activate && uvicorn src.main:app --reload

# 프론트엔드
cd frontend && npm run dev

# 테스트 워치
cd backend && pytest-watch

# 데이터베이스 콘솔
psql $DATABASE_URL
```

### 프로덕션 빌드

```bash
# 백엔드
cd backend && pip install -r requirements.txt && alembic upgrade head

# 프론트엔드
cd frontend && npm run build && npm start
```

---

## 다음 단계

1. **사양서 읽기**:
   - [기능 사양서](./spec.md) - 사용자 요구사항
   - [데이터 모델](./data-model.md) - 데이터베이스 설계
   - [API 사양서](./contracts/api-spec.yaml) - API 계약

2. **예제 코드 탐색**:
   - 시드 스크립트를 실행하여 샘플 데이터 채우기
   - Swagger UI (`/docs`)를 사용하여 API 엔드포인트 테스트
   - UI를 통해 여행 계획 생성 시도

3. **개발 워크플로우 설정**:
   - 린터 및 포매터로 IDE 구성
   - 프리커밋 체크를 위한 Git 훅 설정
   - 권장 VS Code 확장 프로그램 설치

4. **팀 합류**:
   - 기여 가이드라인 읽기
   - 사용 가능한 작업에 대한 프로젝트 보드 확인
   - 질문이 있으면 Slack/Discord로 연락

---

## 추가 리소스

- **LangChain 문서**: https://python.langchain.com/
- **FastAPI 문서**: https://fastapi.tiangolo.com/
- **Next.js 문서**: https://nextjs.org/docs
- **Supabase 문서**: https://supabase.com/docs
- **Mapbox GL JS**: https://docs.mapbox.com/mapbox-gl-js/

---

**즐거운 코딩 되세요!** 🚀

여기에서 다루지 않은 문제가 발생하면 이슈를 생성하거나 팀에 문의하세요.
