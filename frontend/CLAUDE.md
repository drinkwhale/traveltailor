# Frontend 개발 가이드라인

AI TravelTailor 프론트엔드 - Next.js 14 기반 AI 여행 일정 생성 웹 애플리케이션

최종 업데이트: 2025-10-23

## 모듈 개요
Next.js 14 App Router + React 18 + TypeScript로 구축된 반응형 웹 애플리케이션으로, 여행 조건 입력, AI 일정 생성 요청, 일정 시각화, 지도 표시, PDF 다운로드, 오프라인 지원 등을 제공합니다.

## 기술 스택
- **언어**: TypeScript 5.6.3
- **프레임워크**: Next.js 14.2.11, React 18.2.0
- **상태 관리**: React Query (@tanstack/react-query 5.59.20)
- **HTTP 클라이언트**: Axios 1.7.7
- **스타일링**: TailwindCSS 3.4.14, CVA (class-variance-authority 0.7.0), clsx 2.1.1, tailwind-merge 2.5.4
- **지도**: Mapbox GL JS 3.7.0, react-map-gl 7.1.7
- **폼 검증**: Zod 3.23.8
- **날짜 처리**: date-fns 4.1.0
- **보안**: DOMPurify 3.1.7 (XSS 방어), isomorphic-dompurify 2.16.0
- **테스트**: Playwright 1.48.2
- **관측성**: Sentry 8.24.0, PostHog 1.132.3
- **패키지 매니저**: pnpm
- **Node 버전**: >=20.11.0

## 디렉토리 구조

```
frontend/
├── src/
│   ├── app/                      # Next.js 14 App Router
│   │   ├── (auth)/              # 인증 관련 페이지 (그룹 라우팅)
│   │   │   ├── login/           # 로그인 페이지 (/login)
│   │   │   └── signup/          # 회원가입 페이지 (/signup)
│   │   ├── (public)/            # 공개 페이지 (그룹 라우팅)
│   │   │   ├── itinerary/[id]/  # 여행 일정 상세 (/itinerary/:id)
│   │   │   └── my-trips/        # 내 여행 목록 (/my-trips)
│   │   ├── layout.tsx           # 루트 레이아웃 (전역 메타데이터, 폰트, 프로바이더)
│   │   ├── page.tsx             # 메인 페이지 (여행 조건 입력 폼)
│   │   └── globals.css          # 전역 CSS (TailwindCSS @layer)
│   │
│   ├── components/               # React 컴포넌트
│   │   ├── ui/                  # 재사용 가능한 UI 컴포넌트
│   │   │   ├── Button.tsx       # 버튼 컴포넌트 (CVA variants)
│   │   │   ├── Input.tsx        # 입력 필드
│   │   │   ├── Select.tsx       # 선택 드롭다운
│   │   │   ├── Card.tsx         # 카드 컨테이너
│   │   │   ├── Modal.tsx        # 모달 다이얼로그
│   │   │   └── Toast.tsx        # 토스트 알림
│   │   ├── ItineraryForm.tsx    # 여행 조건 입력 폼 (목적지, 날짜, 예산, 선호도)
│   │   ├── ItineraryTimeline.tsx # 일정 타임라인 표시
│   │   ├── ItineraryDayView.tsx # 일자별 일정 상세 뷰
│   │   ├── MapView.tsx          # Mapbox 지도 컴포넌트 (경로 시각화)
│   │   ├── PlaceCard.tsx        # 장소 카드 (이름, 주소, 사진, 평점)
│   │   ├── LoadingSpinner.tsx   # 로딩 인디케이터
│   │   ├── ErrorBoundary.tsx    # 에러 바운더리
│   │   └── OfflineIndicator.tsx # 오프라인 상태 표시
│   │
│   ├── hooks/                    # 커스텀 훅
│   │   ├── useItinerary.ts      # React Query 기반 일정 API 훅
│   │   ├── useAuth.ts           # 인증 상태 관리 훅
│   │   ├── useMap.ts            # Mapbox 지도 제어 훅
│   │   ├── usePlaces.ts         # 장소 검색 훅
│   │   ├── useOffline.ts        # 오프라인 상태 감지 훅
│   │   └── useLocalStorage.ts   # LocalStorage 동기화 훅
│   │
│   ├── lib/                      # 유틸리티 및 헬퍼
│   │   ├── api-client.ts        # Axios 인스턴스 및 인터셉터
│   │   ├── query-client.ts      # React Query 클라이언트 설정
│   │   ├── mapbox.ts            # Mapbox 초기화 및 헬퍼
│   │   ├── validation.ts        # Zod 스키마 정의 (폼 검증)
│   │   ├── formatting.ts        # 날짜, 금액, 거리 포맷팅
│   │   ├── offline.ts           # Service Worker + IndexedDB 큐
│   │   └── utils.ts             # cn() 헬퍼, 범용 유틸리티
│   │
│   └── services/                 # API 클라이언트
│       ├── api.ts               # 통합 API 클라이언트 (CSRF 토큰 처리)
│       ├── auth-service.ts      # 인증 API (회원가입, 로그인, 로그아웃)
│       ├── trip-service.ts      # 여행 일정 API (CRUD, PDF 생성)
│       ├── place-service.ts     # 장소 검색 API
│       └── map-service.ts       # Mapbox Directions API
│
├── public/                       # 정적 에셋
│   ├── sw.js                    # Service Worker (캐시 전략)
│   ├── manifest.json            # PWA 매니페스트
│   ├── icons/                   # 앱 아이콘 (PWA)
│   └── images/                  # 이미지 에셋
│
├── tests/                        # Playwright E2E 테스트
│   ├── auth.spec.ts             # 인증 플로우 테스트
│   ├── itinerary.spec.ts        # 일정 생성 플로우 테스트
│   └── map.spec.ts              # 지도 인터랙션 테스트
│
├── package.json                  # Node 의존성 및 스크립트
├── tsconfig.json                 # TypeScript 설정
├── tailwind.config.ts            # TailwindCSS 설정
├── next.config.js                # Next.js 설정 (Sentry, 이미지 최적화)
├── .env.local.example            # 환경 변수 템플릿
└── README.md                     # 프론트엔드 실행 가이드
```

## 핵심 파일 설명

### App Router 페이지
- **[src/app/layout.tsx](src/app/layout.tsx:1)**: 루트 레이아웃. HTML 메타데이터, 폰트, React Query/Sentry 프로바이더 설정
- **[src/app/page.tsx](src/app/page.tsx:1)**: 메인 페이지. `ItineraryForm` 렌더링, 여행 조건 입력 및 AI 생성 요청
- **[src/app/(public)/itinerary/[id]/page.tsx](src/app/(public)/itinerary/[id]/page.tsx:1)**: 일정 상세 페이지. `ItineraryTimeline`, `MapView`, PDF 다운로드 버튼

### 주요 컴포넌트
- **[src/components/ItineraryForm.tsx](src/components/ItineraryForm.tsx:1)**: 여행 조건 입력 폼. Zod 검증, React Query mutation으로 API 호출
- **[src/components/MapView.tsx](src/components/MapView.tsx:1)**: Mapbox GL JS 지도. 장소 마커, 경로 선, 팝업 표시
- **[src/components/ItineraryTimeline.tsx](src/components/ItineraryTimeline.tsx:1)**: 일자별 일정 타임라인. 시간대별 장소 표시
- **[src/components/ui/Button.tsx](src/components/ui/Button.tsx:1)**: CVA 기반 버튼 컴포넌트. variant (primary/secondary/ghost), size (sm/md/lg)

### 커스텀 훅
- **[src/hooks/useItinerary.ts](src/hooks/useItinerary.ts:1)**: React Query 훅. `useQuery`로 일정 조회, `useMutation`으로 생성/수정/삭제
- **[src/hooks/useAuth.ts](src/hooks/useAuth.ts:1)**: 인증 상태 관리. JWT 토큰 저장, 로그인/로그아웃 처리
- **[src/hooks/useOffline.ts](src/hooks/useOffline.ts:1)**: `navigator.onLine` 감지, 오프라인 시 IndexedDB 큐에 저장

### API 클라이언트
- **[src/services/api.ts](src/services/api.ts:52)**: Axios 인스턴스. CSRF 토큰 자동 포함, 응답 Zod 검증, 에러 처리
- **[src/services/trip-service.ts](src/services/trip-service.ts:1)**: 여행 일정 API 래퍼. `createTrip`, `getTrip`, `generatePDF` 등

### 유틸리티
- **[src/lib/offline.ts](src/lib/offline.ts:1)**: Service Worker 등록, IndexedDB 큐 관리, 온라인 복귀 시 동기화
- **[src/lib/validation.ts](src/lib/validation.ts:1)**: Zod 스키마 정의. `ItineraryFormSchema`, `TripResponseSchema` 등
- **[src/lib/utils.ts](src/lib/utils.ts:1)**: `cn()` 헬퍼 (clsx + tailwind-merge), 날짜/금액 포맷팅

### Service Worker
- **[public/sw.js](public/sw.js:1)**: 캐시 전략 구현
  - **Cache First**: 정적 에셋 (JS, CSS, 이미지, 폰트)
  - **Network First**: API 요청 (최신 데이터 우선, 실패 시 캐시)
  - **Stale-While-Revalidate**: HTML 페이지 (캐시 반환 후 백그라운드 업데이트)

## 주요 명령어

### 개발 환경 설정
```bash
cd frontend
pnpm install                      # 의존성 설치
pnpm exec playwright install --with-deps  # Playwright 브라우저 설치
```

### 환경 변수 설정
```bash
cp .env.local.example .env.local
# 필수 환경 변수:
# - NEXT_PUBLIC_API_URL: 백엔드 API URL (예: http://localhost:8000)
# - NEXT_PUBLIC_MAPBOX_TOKEN: Mapbox 액세스 토큰
# 선택 환경 변수:
# - NEXT_PUBLIC_SENTRY_DSN: Sentry DSN (에러 리포팅)
# - NEXT_PUBLIC_POSTHOG_KEY: PostHog API Key (분석)
# - NEXT_PUBLIC_POSTHOG_HOST: PostHog 호스트 (기본: https://app.posthog.com)
```

### 서버 실행
```bash
# 개발 서버 (핫 리로드 활성화)
pnpm dev  # http://localhost:3000

# 프로덕션 빌드
pnpm build

# 프로덕션 서버 실행
pnpm start
```

### 테스트 및 코드 품질
```bash
# ESLint 실행
pnpm lint

# TypeScript 타입 체킹
pnpm type-check

# Playwright E2E 테스트 실행
pnpm exec playwright test

# Playwright UI 모드 (디버깅)
pnpm exec playwright test --ui

# Playwright 헤드풀 모드 (브라우저 보이기)
pnpm exec playwright test --headed
```

### 빌드 최적화
```bash
# 번들 분석
ANALYZE=true pnpm build

# 타입 체킹 + 빌드
pnpm type-check && pnpm build
```

## 코드 스타일 및 규칙

### 네이밍 컨벤션
- **컴포넌트**: PascalCase (예: `ItineraryForm.tsx`, `MapView.tsx`)
- **훅**: camelCase, `use`로 시작 (예: `useItinerary.ts`, `useAuth.ts`)
- **유틸리티 함수**: camelCase (예: `formatDate`, `calculateDistance`)
- **상수**: UPPER_SNAKE_CASE (예: `API_BASE_URL`, `MAPBOX_TOKEN`)
- **타입/인터페이스**: PascalCase (예: `Trip`, `Place`, `ItineraryFormData`)

### 파일 구조
- **컴포넌트**: 하나의 파일에 하나의 컴포넌트. 관련 타입은 같은 파일에 정의
  ```typescript
  // ItineraryForm.tsx
  interface ItineraryFormProps {
    onSubmit: (data: ItineraryFormData) => void;
  }

  export function ItineraryForm({ onSubmit }: ItineraryFormProps) {
    // ...
  }
  ```

- **훅**: 하나의 파일에 하나의 훅. 관련 타입은 같은 파일에 정의
  ```typescript
  // useItinerary.ts
  interface UseItineraryOptions {
    tripId: string;
  }

  export function useItinerary({ tripId }: UseItineraryOptions) {
    // ...
  }
  ```

### 타입 힌팅
- **모든 함수에 타입 명시**: 매개변수, 반환값
  ```typescript
  function formatDate(date: Date): string {
    return format(date, 'yyyy-MM-dd');
  }
  ```

- **React 컴포넌트 타입**: `React.FC` 대신 함수 선언 + Props 인터페이스
  ```typescript
  interface ButtonProps {
    children: React.ReactNode;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
  }

  export function Button({ children, onClick, variant = 'primary' }: ButtonProps) {
    // ...
  }
  ```

- **타입 vs 인터페이스**:
  - Props, API 응답: `interface` 사용 (확장 가능)
  - Union, Utility 타입: `type` 사용

### 스타일링
- **TailwindCSS 유틸리티 클래스**: 인라인 스타일 대신 Tailwind 클래스 사용
  ```tsx
  <div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow-md">
    <Button variant="primary">생성</Button>
  </div>
  ```

- **CVA (class-variance-authority)**: variant 기반 스타일링
  ```typescript
  const buttonVariants = cva(
    "px-4 py-2 rounded-md font-medium transition-colors",
    {
      variants: {
        variant: {
          primary: "bg-blue-600 text-white hover:bg-blue-700",
          secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
        },
      },
    }
  );
  ```

- **cn() 헬퍼**: 조건부 클래스 병합
  ```typescript
  import { cn } from '@/lib/utils';

  <div className={cn("base-class", isActive && "active-class", className)} />
  ```

## 중요 규칙 및 제약사항

### API 통신
1. **CSRF 토큰**: 모든 POST/PUT/DELETE 요청에 `X-CSRF-Token` 헤더 자동 포함
   - [src/services/api.ts:52](src/services/api.ts#L52)에서 인터셉터로 처리
   - 토큰은 `GET /v1/csrf-token`에서 가져와 메모리에 저장

2. **응답 검증**: 모든 API 응답은 Zod 스키마로 검증
   ```typescript
   const TripResponseSchema = z.object({
     id: z.string(),
     destination: z.string(),
     startDate: z.string().datetime(),
     // ...
   });

   const response = await api.get('/v1/trips/123');
   const trip = TripResponseSchema.parse(response.data);
   ```

3. **에러 처리**: Axios 인터셉터에서 공통 에러 처리, Sentry 자동 리포팅
   ```typescript
   api.interceptors.response.use(
     (response) => response,
     (error) => {
       if (error.response?.status === 401) {
         // 인증 실패 시 로그인 페이지로 리디렉션
         router.push('/login');
       }
       Sentry.captureException(error);
       return Promise.reject(error);
     }
   );
   ```

### 상태 관리
1. **React Query**: 서버 상태 관리
   - `useQuery`: 데이터 조회 (캐싱, 자동 리페치)
   - `useMutation`: 데이터 변경 (낙관적 업데이트 지원)
   ```typescript
   const { data: trip, isLoading } = useQuery({
     queryKey: ['trip', tripId],
     queryFn: () => tripService.getTrip(tripId),
   });

   const createMutation = useMutation({
     mutationFn: tripService.createTrip,
     onSuccess: () => queryClient.invalidateQueries(['trips']),
   });
   ```

2. **LocalStorage**: 로컬 상태 지속성 (JWT 토큰, 사용자 선호도)
   ```typescript
   const useLocalStorage = <T>(key: string, initialValue: T) => {
     const [value, setValue] = useState<T>(() => {
       const stored = localStorage.getItem(key);
       return stored ? JSON.parse(stored) : initialValue;
     });

     useEffect(() => {
       localStorage.setItem(key, JSON.stringify(value));
     }, [key, value]);

     return [value, setValue] as const;
   };
   ```

### 지도
1. **Mapbox 토큰**: 환경 변수에서만 로드, 하드코딩 금지
   ```typescript
   const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
   if (!MAPBOX_TOKEN) {
     throw new Error('NEXT_PUBLIC_MAPBOX_TOKEN is not defined');
   }
   ```

2. **지도 인스턴스 재사용**: 컴포넌트 마운트 시 한 번만 생성, 언마운트 시 정리
   ```typescript
   useEffect(() => {
     const map = new mapboxgl.Map({
       container: mapContainer.current,
       style: 'mapbox://styles/mapbox/streets-v12',
       center: [lng, lat],
       zoom: 12,
     });

     return () => map.remove();
   }, []);
   ```

3. **마커 관리**: 경로 변경 시 기존 마커 제거 후 새로 생성
   ```typescript
   // 기존 마커 제거
   markers.current.forEach(marker => marker.remove());
   markers.current = [];

   // 새 마커 생성
   places.forEach(place => {
     const marker = new mapboxgl.Marker()
       .setLngLat([place.longitude, place.latitude])
       .addTo(map);
     markers.current.push(marker);
   });
   ```

### 오프라인 지원
1. **Service Worker 등록**: [src/lib/offline.ts](src/lib/offline.ts:1)에서 초기화
   ```typescript
   if ('serviceWorker' in navigator) {
     navigator.serviceWorker.register('/sw.js')
       .then(registration => console.log('SW registered:', registration))
       .catch(error => console.error('SW registration failed:', error));
   }
   ```

2. **IndexedDB 큐**: 오프라인 시 요청을 큐에 저장, 온라인 복귀 시 재시도
   ```typescript
   const db = await openDB('offline-queue', 1, {
     upgrade(db) {
       db.createObjectStore('requests', { keyPath: 'id', autoIncrement: true });
     },
   });

   // 오프라인 시 큐에 저장
   if (!navigator.onLine) {
     await db.add('requests', { url, method, data, timestamp: Date.now() });
   }

   // 온라인 복귀 시 재시도
   window.addEventListener('online', async () => {
     const requests = await db.getAll('requests');
     for (const request of requests) {
       await api.request(request);
       await db.delete('requests', request.id);
     }
   });
   ```

3. **캐시 전략**: [public/sw.js](public/sw.js:1)에서 정의
   - **Cache First**: 정적 에셋 (JS, CSS, 이미지) → 빠른 로딩
   - **Network First**: API 요청 → 최신 데이터 우선
   - **Stale-While-Revalidate**: HTML 페이지 → 캐시 반환 후 백그라운드 업데이트

### 보안
1. **XSS 방어**: DOMPurify로 사용자 입력 sanitize
   ```typescript
   import DOMPurify from 'isomorphic-dompurify';

   const sanitizedHTML = DOMPurify.sanitize(userInput);
   return <div dangerouslySetInnerHTML={{ __html: sanitizedHTML }} />;
   ```

2. **환경 변수**: 클라이언트 노출 변수는 `NEXT_PUBLIC_` 접두사 필수
   - ✅ `NEXT_PUBLIC_API_URL` (클라이언트 접근 가능)
   - ❌ `API_SECRET_KEY` (서버 전용, 클라이언트 접근 불가)

3. **HTTPS**: 프로덕션에서 HTTPS 강제 (Next.js 헤더 설정)
   ```javascript
   // next.config.js
   module.exports = {
     async headers() {
       return [
         {
           source: '/:path*',
           headers: [
             { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
           ],
         },
       ];
     },
   };
   ```

### 성능 최적화
1. **이미지 최적화**: Next.js `<Image>` 컴포넌트 사용
   ```tsx
   import Image from 'next/image';

   <Image
     src="/images/place.jpg"
     alt="Place"
     width={400}
     height={300}
     loading="lazy"
   />
   ```

2. **코드 스플리팅**: 동적 import로 번들 크기 감소
   ```typescript
   import dynamic from 'next/dynamic';

   const MapView = dynamic(() => import('@/components/MapView'), {
     loading: () => <LoadingSpinner />,
     ssr: false, // Mapbox는 클라이언트 전용
   });
   ```

3. **React Query 캐싱**: `staleTime`, `cacheTime` 설정으로 불필요한 리페치 방지
   ```typescript
   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 5 * 60 * 1000, // 5분
         cacheTime: 10 * 60 * 1000, // 10분
       },
     },
   });
   ```

### 접근성 (A11y)
1. **시맨틱 HTML**: `<div>` 대신 적절한 시맨틱 태그 사용
   ```tsx
   <article>
     <header><h2>여행 일정</h2></header>
     <section>...</section>
   </article>
   ```

2. **ARIA 속성**: 인터랙티브 요소에 적절한 ARIA 레이블
   ```tsx
   <button aria-label="일정 생성" aria-pressed={isActive}>
     생성
   </button>
   ```

3. **키보드 네비게이션**: 모든 인터랙티브 요소 키보드 접근 가능
   ```tsx
   <div
     role="button"
     tabIndex={0}
     onKeyDown={(e) => e.key === 'Enter' && onClick()}
   >
     클릭
   </div>
   ```

## 모니터링 및 관측성

### Sentry
- **DSN**: `NEXT_PUBLIC_SENTRY_DSN` 환경 변수 설정
- **초기화**: [src/app/layout.tsx](src/app/layout.tsx:1)에서 `Sentry.init()`
- **에러 캡처**: React Error Boundary + 전역 에러 리스너
  ```typescript
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 1.0,
  });
  ```

### PostHog
- **API Key**: `NEXT_PUBLIC_POSTHOG_KEY` 환경 변수 설정
- **이벤트 추적**: 사용자 행동 추적 (페이지 뷰, 버튼 클릭, 일정 생성 등)
  ```typescript
  import posthog from 'posthog-js';

  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com',
  });

  // 이벤트 추적
  posthog.capture('trip_created', { destination, budget });
  ```

### Web Vitals
- **Core Web Vitals 추적**: Next.js 내장 `reportWebVitals` 사용
  ```typescript
  // src/app/layout.tsx
  export function reportWebVitals(metric: NextWebVitalsMetric) {
    console.log(metric);
    posthog.capture('web_vitals', metric);
  }
  ```

## 테스트

### Playwright E2E 테스트
- **설정**: [playwright.config.ts](playwright.config.ts:1)에서 브라우저, 베이스 URL 설정
- **테스트 작성**: [tests/itinerary.spec.ts](tests/itinerary.spec.ts:1) 참고
  ```typescript
  import { test, expect } from '@playwright/test';

  test('사용자가 여행 일정을 생성할 수 있다', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="destination"]', '도쿄');
    await page.click('button:has-text("생성")');
    await expect(page.locator('h1')).toContainText('여행 일정');
  });
  ```

### 테스트 커버리지
- **목표**: 주요 플로우 80% 이상 커버
- **우선순위**: 인증, 일정 생성, 지도 인터랙션

## 배포
- **Vercel**: Next.js 최적화 플랫폼 (권장)
- **환경 변수**: Vercel 대시보드에서 설정 또는 GitHub Secrets
- **빌드 명령어**: `pnpm build`
- **출력 디렉토리**: `.next/`
- **헬스체크**: `GET /api/health` (서버 상태 확인)

## 문제 해결

### 자주 발생하는 오류

1. **Module not found: Can't resolve '@/...'**
   - 해결: `tsconfig.json`의 `paths` 설정 확인, `pnpm install` 재실행

2. **Hydration failed because the initial UI does not match**
   - 해결: 클라이언트/서버 렌더링 불일치. `useEffect`로 클라이언트 전용 코드 이동 또는 `suppressHydrationWarning` 사용

3. **Mapbox token is invalid**
   - 해결: `.env.local`의 `NEXT_PUBLIC_MAPBOX_TOKEN` 확인

4. **CSRF token missing or invalid**
   - 해결: [src/services/api.ts](src/services/api.ts:52)의 CSRF 인터셉터 확인, `/v1/csrf-token` 엔드포인트 호출 확인

5. **Service Worker not updating**
   - 해결: 브라우저에서 Service Worker 수동 제거 (Application → Service Workers → Unregister) 후 새로고침

## 추가 리소스
- [Next.js 공식 문서](https://nextjs.org/docs)
- [React Query 문서](https://tanstack.com/query/latest/docs/react/overview)
- [TailwindCSS 문서](https://tailwindcss.com/docs)
- [Mapbox GL JS 문서](https://docs.mapbox.com/mapbox-gl-js/guides/)
- [Playwright 문서](https://playwright.dev/docs/intro)
- [Zod 문서](https://zod.dev/)
