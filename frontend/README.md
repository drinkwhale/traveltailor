# AI TravelTailor Frontend

맞춤형 여행 일정 생성 UI를 제공하는 Next.js 14 + React 18 애플리케이션입니다. Supabase 인증, 백엔드 API, Mapbox 지도를 통합합니다.

## 주요 기술 스택
- Next.js 14 (App Router)
- React 18 + TypeScript 5
- Tailwind CSS, Shadcn UI
- React Query, Mapbox GL JS

## 요구 사항
- Node.js 20.11 이상
- `pnpm` 9.x (권장) 또는 npm 10.x
- 백엔드 API(`http://localhost:8000`)가 실행 중이어야 주요 기능을 확인할 수 있습니다.

## 환경 변수
다음 명령으로 템플릿을 복사한 뒤 값을 채워 주세요.

```bash
cp .env.local.example .env.local
```

필수 값
- `NEXT_PUBLIC_API_URL`: 백엔드 FastAPI 서버 URL
- `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN`

Analytics 등 선택 항목은 필요 시 채워 넣습니다.

## 설치 & 실행

```bash
# 의존성 설치
pnpm install          # npm 사용 시 npm install

# 개발 서버
pnpm dev              # http://localhost:3000
```

## 품질 검사 & 빌드

```bash
pnpm lint             # ESLint
pnpm type-check       # TypeScript 타입 검사
pnpm build            # 프로덕션 빌드
pnpm start            # 빌드 결과 실행

# Playwright E2E 테스트
pnpm exec playwright test
```

## 참고 문서
- 백엔드 연동 및 API 명세: `specs/001-ai-travel-planner/spec.md`
- 구현 계획과 작업 현황: `specs/001-ai-travel-planner/plan.md`, `specs/001-ai-travel-planner/tasks.md`
