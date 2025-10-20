# 작업 목록: AI TravelTailor - 개인 맞춤형 여행 설계 서비스

**입력**: `/specs/001-ai-travel-planner/`의 설계 문서
**사전 요구사항**: plan.md (필수), spec.md (필수), research.md, data-model.md, contracts/
**테스트**: 이 프로젝트에는 명시적인 TDD 요구사항이 없으므로 테스트 작업은 선택사항입니다.

## 작업 형식: `[ID] [P?] [Story] 설명`
- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 이 작업이 속한 사용자 스토리 (예: US1, US2, US3)
- 설명에 정확한 파일 경로 포함

## 경로 규칙
- **백엔드**: `backend/src/`, `backend/tests/`
- **프론트엔드**: `frontend/src/`, `frontend/tests/`
- **공유**: `shared/types/`, `shared/schemas/`

---

## Phase 1: 프로젝트 초기 설정 (공유 인프라)

**목적**: 프로젝트 초기화 및 기본 구조 생성

- [x] T001 plan.md에 따라 프로젝트 디렉토리 구조 생성 (backend/, frontend/, shared/)
- [x] T002 [P] 백엔드 Python 프로젝트 초기화 (FastAPI, requirements.txt)
- [x] T003 [P] 프론트엔드 Next.js 15 프로젝트 초기화 (TypeScript, Tailwind CSS)
- [x] T004 [P] 공유 TypeScript 타입 패키지 설정 in shared/types/
- [x] T005 [P] 백엔드 린팅 설정 (black, ruff, mypy) in backend/
- [x] T006 [P] 프론트엔드 린팅 설정 (ESLint, Prettier) in frontend/
- [x] T007 환경 변수 템플릿 생성 (backend/.env.example, frontend/.env.local.example)
- [x] T008 Git 설정 (.gitignore, pre-commit hooks)

---

## Phase 2: 기반 인프라 (모든 스토리의 선행 요구사항)

**목적**: 모든 사용자 스토리가 의존하는 핵심 인프라 - 이 단계 완료 전에는 스토리 작업 불가

**⚠️ 중요**: 이 단계가 완료되어야 사용자 스토리 작업 시작 가능

### 데이터베이스 및 인증 (FR-014 지원)

- [ ] T009 Supabase 프로젝트 설정 및 연결 구성
- [ ] T010 Alembic 마이그레이션 프레임워크 설정 in backend/alembic/
- [ ] T011 User 모델 및 테이블 생성 in backend/src/models/user.py
- [ ] T012 UserPreference 모델 및 테이블 생성 in backend/src/models/user_preference.py
- [ ] T013 데이터베이스 마이그레이션 스크립트 작성 (users, user_preferences)
- [ ] T014 Supabase Auth 설정 (이메일/비밀번호 인증)
- [ ] T015 JWT 인증 미들웨어 구현 in backend/src/core/security.py
- [ ] T016 인증 API 엔드포인트 구현 in backend/src/api/v1/auth.py (회원가입, 로그인, 프로필 조회)

### 백엔드 핵심 인프라

- [ ] T017 [P] FastAPI 앱 초기화 및 라우터 구조 in backend/src/main.py
- [ ] T018 [P] 데이터베이스 연결 관리자 in backend/src/core/database.py
- [ ] T019 [P] 전역 에러 핸들링 및 로깅 설정 in backend/src/core/exceptions.py
- [ ] T020 [P] API 응답 스키마 기본 구조 in backend/src/schemas/base.py
- [ ] T021 [P] 환경 설정 관리 in backend/src/config.py

### 프론트엔드 핵심 인프라

- [ ] T022 [P] Next.js 레이아웃 및 라우팅 구조 설정 in frontend/src/app/layout.tsx
- [ ] T023 [P] Supabase 클라이언트 설정 in frontend/src/lib/supabase.ts
- [ ] T024 [P] API 클라이언트 기본 구조 (Axios/Fetch) in frontend/src/services/api.ts
- [ ] T025 [P] 인증 서비스 및 훅 in frontend/src/services/auth.ts, frontend/src/hooks/useAuth.ts
- [ ] T026 [P] 로그인/회원가입 페이지 in frontend/src/app/login/page.tsx, frontend/src/app/register/page.tsx
- [ ] T027 [P] Tailwind CSS 및 기본 스타일 설정 in frontend/tailwind.config.ts
- [ ] T028 [P] Shadcn UI 컴포넌트 라이브러리 설치 및 설정

### 외부 API 통합 기초

- [ ] T029 [P] Google Places API 클라이언트 기본 구조 in backend/src/integrations/google_maps.py
- [ ] T030 [P] OpenAI/LangChain 클라이언트 기본 구조 in backend/src/services/ai/__init__.py
- [ ] T031 [P] Mapbox 설정 in frontend/src/lib/mapbox.ts

**체크포인트**: 기반 인프라 완료 - 이제 사용자 스토리 병렬 작업 시작 가능

---

## Phase 3: User Story 1 - AI 여행 일정 자동 생성 (Priority: P1) 🎯 MVP

**목표**: 사용자가 여행 조건을 입력하면 AI가 숙소, 관광지, 식당, 이동 경로가 포함된 완전한 여행 일정을 30초 이내에 자동 생성

**독립 테스트**: "3박 4일, 도쿄, 예산 80만원, 커플 여행, 맛집 중심"을 입력하여 날짜별/시간대별 완전한 여행 일정을 받아볼 수 있는지 확인

**요구사항 매핑**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-018, FR-019, FR-020

### 데이터 모델 (US1)

- [ ] T032 [P] [US1] TravelPlan 모델 생성 in backend/src/models/travel_plan.py
- [ ] T033 [P] [US1] DailyItinerary 모델 생성 in backend/src/models/daily_itinerary.py
- [ ] T034 [P] [US1] Place 모델 생성 in backend/src/models/place.py
- [ ] T035 [P] [US1] ItineraryPlace 모델 생성 in backend/src/models/itinerary_place.py
- [ ] T036 [P] [US1] Route 모델 생성 in backend/src/models/route.py
- [ ] T037 [US1] 데이터베이스 마이그레이션 스크립트 작성 (travel_plans, daily_itineraries, places, itinerary_places, routes)
- [ ] T038 [US1] 마이그레이션 실행 및 검증

### Pydantic 스키마 (US1)

- [ ] T039 [P] [US1] TravelPlan 요청/응답 스키마 in backend/src/schemas/travel_plan.py
- [ ] T040 [P] [US1] Place 스키마 in backend/src/schemas/place.py
- [ ] T041 [P] [US1] DailyItinerary 스키마 in backend/src/schemas/itinerary.py

### AI 여행 계획 서비스 (US1 핵심 로직)

- [ ] T042 [US1] LangChain 프롬프트 템플릿 설계 in backend/src/services/ai/prompts.py
- [ ] T043 [US1] 사용자 입력 분석 서비스 (선호도 추출) in backend/src/services/ai/preference_analyzer.py
- [ ] T044 [US1] 예산 할당 로직 (숙박/식사/관광/교통) in backend/src/services/ai/budget_allocator.py
- [ ] T045 [US1] Google Places API 장소 검색 서비스 in backend/src/integrations/google_maps.py (검색, 상세 조회)
- [ ] T046 [US1] AI 장소 추천 및 랭킹 로직 in backend/src/services/places/recommender.py
- [ ] T047 [US1] 경로 최적화 서비스 (방문 순서 계산) in backend/src/services/routes/optimizer.py
- [ ] T048 [US1] 시간대별 일정 생성 서비스 in backend/src/services/ai/timeline_generator.py
- [ ] T049 [US1] 통합 여행 계획 생성 서비스 in backend/src/services/ai/planner.py (T042~T048 통합)

### API 엔드포인트 (US1)

- [ ] T050 [US1] POST /v1/travel-plans 엔드포인트 구현 (비동기 생성 시작) in backend/src/api/v1/travel_plans.py
- [ ] T051 [US1] GET /v1/travel-plans/{planId}/status 엔드포인트 (생성 상태 조회) in backend/src/api/v1/travel_plans.py
- [ ] T052 [US1] GET /v1/travel-plans/{planId} 엔드포인트 (상세 조회) in backend/src/api/v1/travel_plans.py
- [ ] T053 [P] [US1] GET /v1/travel-plans 엔드포인트 (목록 조회) in backend/src/api/v1/travel_plans.py
- [ ] T054 [P] [US1] PATCH /v1/travel-plans/{planId} 엔드포인트 (수정) in backend/src/api/v1/travel_plans.py
- [ ] T055 [P] [US1] DELETE /v1/travel-plans/{planId} 엔드포인트 (삭제) in backend/src/api/v1/travel_plans.py

### 프론트엔드 - 여행 계획 생성 UI (US1)

- [ ] T056 [P] [US1] TravelPlan TypeScript 타입 정의 in shared/types/travel-plan.ts
- [ ] T057 [US1] 여행 계획 API 클라이언트 서비스 in frontend/src/services/travel-plans.ts
- [ ] T058 [US1] 여행 입력 폼 컴포넌트 in frontend/src/components/forms/TravelPlanForm.tsx
- [ ] T059 [US1] 여행 생성 페이지 in frontend/src/app/(auth)/create/page.tsx
- [ ] T060 [US1] 생성 진행 상태 표시 컴포넌트 in frontend/src/components/ui/ProgressIndicator.tsx
- [ ] T061 [US1] useTravelPlan 커스텀 훅 (생성, 조회, 상태 폴링) in frontend/src/hooks/useTravelPlan.ts

### 프론트엔드 - 여행 일정 표시 UI (US1)

- [ ] T062 [US1] 일정 상세 보기 페이지 in frontend/src/app/(auth)/plan/[id]/page.tsx
- [ ] T063 [P] [US1] 일일 타임라인 컴포넌트 in frontend/src/components/timeline/DailyTimeline.tsx
- [ ] T064 [P] [US1] 장소 카드 컴포넌트 in frontend/src/components/timeline/PlaceCard.tsx
- [ ] T065 [P] [US1] 예산 요약 컴포넌트 in frontend/src/components/budget/BudgetSummary.tsx

### 에러 처리 및 검증 (US1)

- [ ] T066 [P] [US1] 입력 데이터 검증 (필수 필드, 날짜 유효성) in backend/src/schemas/travel_plan.py
- [ ] T067 [P] [US1] 예산 부족 경고 로직 in backend/src/services/ai/budget_allocator.py
- [ ] T068 [P] [US1] 목적지 데이터 부족 경고 in backend/src/services/places/recommender.py
- [ ] T069 [US1] 프론트엔드 에러 핸들링 및 사용자 피드백 in frontend/src/components/forms/TravelPlanForm.tsx

**체크포인트**: User Story 1 완료 - 사용자가 여행 조건을 입력하여 완전한 AI 생성 일정을 받을 수 있어야 함

---

## Phase 4: User Story 2 - 지도 기반 경로 시각화 및 내보내기 (Priority: P2)

**목표**: 생성된 여행 일정을 지도 위에 시각화하고, 카카오맵/구글맵으로 내보내기 기능 제공

**독립 테스트**: 생성된 여행 일정에서 "지도 보기"를 클릭하여 장소와 경로를 확인하고, "카카오맵으로 내보내기" 버튼으로 외부 앱에 전송 가능한지 확인

**요구사항 매핑**: FR-007, FR-008, FR-009

### 백엔드 - 지도 데이터 API (US2)

- [ ] T070 [P] [US2] 경로 계산 서비스 (Mapbox Directions API 통합) in backend/src/integrations/mapbox.py
- [ ] T071 [P] [US2] 경로 폴리라인 인코딩 유틸리티 in backend/src/core/geo_utils.py
- [ ] T072 [US2] 지도 내보내기 URL 생성 서비스 in backend/src/services/exports/map_exporter.py
- [ ] T073 [US2] GET /v1/exports/map/{planId} 엔드포인트 in backend/src/api/v1/exports.py

### 프론트엔드 - 지도 시각화 (US2)

- [ ] T074 [US2] Mapbox GL JS 설정 및 초기화 in frontend/src/lib/mapbox.ts
- [ ] T075 [US2] MapView 컴포넌트 (장소 마커 표시) in frontend/src/components/map/MapView.tsx
- [ ] T076 [US2] RouteMap 컴포넌트 (경로 라인 표시) in frontend/src/components/map/RouteMap.tsx
- [ ] T077 [US2] 장소 마커 클릭 시 상세 정보 팝업 in frontend/src/components/map/PlacePopup.tsx
- [ ] T078 [US2] 경로 정보 표시 (이동 시간, 거리) in frontend/src/components/map/RouteInfo.tsx

### 프론트엔드 - 외부 지도 내보내기 (US2)

- [ ] T079 [P] [US2] 카카오맵 URL 생성 유틸리티 in frontend/src/lib/kakao-map-link.ts
- [ ] T080 [P] [US2] 구글맵 URL 생성 유틸리티 in frontend/src/lib/google-map-link.ts
- [ ] T081 [US2] 지도 내보내기 버튼 컴포넌트 in frontend/src/components/map/ExportButtons.tsx
- [ ] T082 [US2] 디바이스 감지 및 적절한 링크 제공 로직 in frontend/src/lib/device-detector.ts

### 통합 (US2)

- [ ] T083 [US2] 여행 일정 상세 페이지에 지도 뷰 통합 in frontend/src/app/(auth)/plan/[id]/page.tsx

**체크포인트**: User Story 2 완료 - 여행 일정의 모든 장소와 경로를 지도에서 확인하고 외부 앱으로 내보낼 수 있어야 함

---

## Phase 5: User Story 3 - 여행 일정표 PDF 생성 및 다운로드 (Priority: P2)

**목표**: 생성된 여행 일정을 브랜딩된 PDF 문서로 다운로드 가능

**독립 테스트**: 여행 일정 화면에서 "PDF 다운로드" 버튼을 클릭하여 10초 이내에 포맷된 PDF 파일을 받을 수 있는지 확인

**요구사항 매핑**: FR-010, FR-011

### 백엔드 - PDF 생성 서비스 (US3)

- [ ] T084 [US3] Puppeteer 설정 및 브라우저 인스턴스 풀 in backend/src/services/pdf/__init__.py
- [ ] T085 [US3] HTML 템플릿 설계 (Tailwind CSS 사용) in backend/src/services/pdf/templates/itinerary.html
- [ ] T086 [US3] Mapbox Static API 통합 (지도 이미지 생성) in backend/src/integrations/mapbox.py
- [ ] T087 [US3] PDF 생성 로직 (HTML → PDF 변환) in backend/src/services/pdf/generator.py
- [ ] T088 [US3] PDF 파일 저장 및 URL 생성 (Supabase Storage) in backend/src/services/pdf/storage.py
- [ ] T089 [US3] GET /v1/exports/pdf/{planId} 엔드포인트 in backend/src/api/v1/exports.py

### 프론트엔드 - PDF 다운로드 UI (US3)

- [ ] T090 [US3] PDF 다운로드 버튼 컴포넌트 in frontend/src/components/exports/PdfDownloadButton.tsx
- [ ] T091 [US3] PDF 미리보기 컴포넌트 (선택사항) in frontend/src/components/pdf/PdfPreview.tsx
- [ ] T092 [US3] 여행 일정 상세 페이지에 PDF 다운로드 기능 통합 in frontend/src/app/(auth)/plan/[id]/page.tsx

### 브랜딩 및 스타일링 (US3)

- [ ] T093 [P] [US3] TravelTailor 로고 및 브랜드 에셋 추가 in backend/src/services/pdf/assets/
- [ ] T094 [P] [US3] PDF 스타일 시트 작성 (Tailwind CSS) in backend/src/services/pdf/templates/styles.css

**체크포인트**: User Story 3 완료 - 여행 일정을 브랜딩된 PDF로 다운로드하여 오프라인에서도 확인 가능해야 함

---

## Phase 6: User Story 4 - 항공편 및 숙박 예약 링크 제공 (Priority: P3)

**목표**: 여행 일정에 항공편 및 숙박 시설의 추천 옵션과 예약 링크 포함

**독립 테스트**: 생성된 여행 일정에서 항공편/숙박 예약 링크를 클릭하여 외부 예약 사이트로 이동 가능한지 확인

**요구사항 매핑**: FR-012, FR-013

### 데이터 모델 (US4)

- [ ] T095 [P] [US4] FlightOption 모델 생성 in backend/src/models/flight_option.py
- [ ] T096 [P] [US4] AccommodationOption 모델 생성 in backend/src/models/accommodation_option.py
- [ ] T097 [US4] 데이터베이스 마이그레이션 스크립트 작성 (flight_options, accommodation_options)

### 외부 API 통합 (US4)

- [ ] T098 [P] [US4] Skyscanner API 클라이언트 in backend/src/integrations/skyscanner.py
- [ ] T099 [P] [US4] Booking.com 제휴 링크 생성 in backend/src/integrations/booking.py
- [ ] T100 [P] [US4] Agoda API 클라이언트 in backend/src/integrations/agoda.py

### 추천 서비스 (US4)

- [ ] T101 [US4] 항공편 검색 및 추천 서비스 in backend/src/services/recommendations/flight_recommender.py
- [ ] T102 [US4] 숙박 검색 및 추천 서비스 in backend/src/services/recommendations/accommodation_recommender.py
- [ ] T103 [US4] 제휴 링크 추적 유틸리티 in backend/src/core/affiliate_tracker.py

### API 엔드포인트 (US4)

- [ ] T104 [P] [US4] GET /v1/recommendations/flights/{planId} 엔드포인트 in backend/src/api/v1/recommendations.py
- [ ] T105 [P] [US4] GET /v1/recommendations/accommodations/{planId} 엔드포인트 in backend/src/api/v1/recommendations.py

### 프론트엔드 UI (US4)

- [ ] T106 [US4] 항공편 추천 카드 컴포넌트 in frontend/src/components/recommendations/FlightCard.tsx
- [ ] T107 [US4] 숙박 추천 카드 컴포넌트 in frontend/src/components/recommendations/AccommodationCard.tsx
- [ ] T108 [US4] 추천 섹션 컴포넌트 in frontend/src/components/recommendations/RecommendationsSection.tsx
- [ ] T109 [US4] 여행 일정 상세 페이지에 추천 섹션 통합 in frontend/src/app/(auth)/plan/[id]/page.tsx

### 에러 처리 (US4)

- [ ] T110 [US4] 외부 API 장애 시 그레이스풀 디그레이데이션 in backend/src/services/recommendations/
- [ ] T111 [US4] 예약 링크 unavailable 시 사용자 피드백 in frontend/src/components/recommendations/

**체크포인트**: User Story 4 완료 - 여행 일정에 항공편 및 숙박 추천 옵션과 예약 링크가 포함되어야 함

---

## Phase 7: User Story 5 - 사용자 맞춤 학습 및 히스토리 관리 (Priority: P3)

**목표**: 사용자의 과거 여행 기록과 선호도를 저장하여, 다음 여행 계획 시 자동으로 반영

**독립 테스트**: 사용자가 두 번째 여행 일정을 생성할 때, 이전 여행에서의 선호도가 자동으로 입력 필드에 미리 채워지는지 확인

**요구사항 매핑**: FR-015, FR-016, FR-017

### 백엔드 - 선호도 학습 및 저장 (US5)

- [ ] T112 [US5] 사용자 선호도 학습 로직 (여행 기록 분석) in backend/src/services/preferences/learning.py
- [ ] T113 [US5] 선호도 자동 업데이트 서비스 (여행 생성 시 트리거) in backend/src/services/preferences/auto_updater.py
- [ ] T114 [P] [US5] GET /v1/preferences 엔드포인트 in backend/src/api/v1/preferences.py
- [ ] T115 [P] [US5] PUT /v1/preferences 엔드포인트 in backend/src/api/v1/preferences.py

### 프론트엔드 - 선호도 관리 UI (US5)

- [ ] T116 [US5] 선호도 설정 페이지 in frontend/src/app/(auth)/preferences/page.tsx
- [ ] T117 [US5] 선호도 폼 컴포넌트 in frontend/src/components/forms/PreferencesForm.tsx
- [ ] T118 [US5] 여행 생성 폼에 자동 선호도 반영 로직 in frontend/src/components/forms/TravelPlanForm.tsx (T058 업데이트)

### 프론트엔드 - 여행 히스토리 (US5)

- [ ] T119 [US5] 여행 히스토리 페이지 in frontend/src/app/(auth)/history/page.tsx
- [ ] T120 [P] [US5] 여행 목록 카드 컴포넌트 in frontend/src/components/history/TravelPlanCard.tsx
- [ ] T121 [P] [US5] 필터 및 정렬 기능 in frontend/src/components/history/FiltersBar.tsx
- [ ] T122 [US5] 과거 여행 상세 조회 및 PDF 재다운로드 기능 통합

**체크포인트**: User Story 5 완료 - 사용자 선호도가 학습되고, 히스토리를 조회하며, 다음 여행 계획 시 자동 반영되어야 함

---

## Phase 8: 성능 최적화 및 마무리

**목적**: 여러 사용자 스토리에 영향을 주는 개선 사항

### 성능 최적화

- [ ] T123 [P] Redis 캐싱 설정 (장소 데이터, 항공편 가격) in backend/src/core/cache.py
- [ ] T124 [P] 데이터베이스 쿼리 최적화 (인덱스 추가, N+1 문제 해결)
- [ ] T125 [P] 프론트엔드 번들 크기 최적화 (코드 스플리팅, 레이지 로딩)
- [ ] T126 API 응답 시간 모니터링 및 최적화 (<200ms 목표)

### 보안 강화

- [ ] T127 [P] Rate limiting 구현 (사용자당 일일 생성 제한) in backend/src/api/dependencies.py
- [ ] T128 [P] 입력 sanitization 및 SQL injection 방어
- [ ] T129 CORS 설정 검토 및 강화 in backend/src/main.py

### 모니터링 및 로깅

- [ ] T130 [P] Sentry 에러 트래킹 설정 (백엔드/프론트엔드)
- [ ] T131 [P] PostHog 분석 설정 (사용자 행동 추적)
- [ ] T132 주요 메트릭 로깅 (AI 생성 시간, API 호출 성공률)

### 문서화

- [ ] T133 [P] API 문서 업데이트 (Swagger UI 확인)
- [ ] T134 [P] README.md 작성 (프로젝트 개요, 실행 방법)
- [ ] T135 quickstart.md 검증 및 업데이트
- [ ] T136 배포 가이드 작성 in docs/deployment.md

### 테스트 (선택사항 - 요청 시 작성)

- [ ] T137 [P] 백엔드 통합 테스트 작성 (주요 API 엔드포인트)
- [ ] T138 [P] 프론트엔드 E2E 테스트 작성 (Playwright) - 여행 생성 플로우
- [ ] T139 외부 API 모킹 및 계약 테스트

### 배포 준비

- [ ] T140 환경 변수 검토 (프로덕션 설정)
- [ ] T141 [P] Vercel 배포 설정 (프론트엔드)
- [ ] T142 [P] Railway/Render 배포 설정 (백엔드)
- [ ] T143 데이터베이스 마이그레이션 프로덕션 실행
- [ ] T144 CI/CD 파이프라인 설정 (GitHub Actions)

---

## 의존성 및 실행 순서

### Phase 의존성

- **프로젝트 초기 설정 (Phase 1)**: 의존성 없음 - 즉시 시작 가능
- **기반 인프라 (Phase 2)**: Phase 1 완료 필요 - **모든 사용자 스토리를 차단**
- **사용자 스토리 (Phase 3~7)**: Phase 2 완료 필요
  - Phase 2 완료 후 모든 스토리 병렬 진행 가능 (인력이 있는 경우)
  - 또는 우선순위 순서로 순차 진행 (P1 → P2 → P3)
- **성능 최적화 및 마무리 (Phase 8)**: 원하는 사용자 스토리가 모두 완료된 후

### 사용자 스토리 의존성

- **User Story 1 (P1)**: Phase 2 완료 후 시작 - 다른 스토리 의존성 없음
- **User Story 2 (P2)**: Phase 2 완료 후 시작 - US1과 통합하지만 독립적으로 테스트 가능
- **User Story 3 (P2)**: Phase 2 완료 후 시작 - US1과 통합하지만 독립적으로 테스트 가능
- **User Story 4 (P3)**: Phase 2 완료 후 시작 - US1과 통합하지만 독립적으로 테스트 가능
- **User Story 5 (P3)**: Phase 2 완료 후 시작 - US1과 통합하지만 독립적으로 테스트 가능

### 각 사용자 스토리 내 의존성

- 모델 → 서비스 → API 엔드포인트 → 프론트엔드 UI 순서
- 핵심 구현 완료 후 통합
- 스토리 완료 후 다음 우선순위로 이동

### 병렬 실행 기회

- 프로젝트 초기 설정 단계의 [P] 작업들 (T002~T006)
- 기반 인프라 단계의 [P] 작업들 (T017~T031)
- Phase 2 완료 후 모든 사용자 스토리 병렬 진행 가능
- 각 스토리 내 모델 생성 작업들 (T032~T036, T095~T096 등)
- 각 스토리 내 Pydantic 스키마 작업들 (T039~T041)
- 각 스토리 내 프론트엔드 컴포넌트들 (T063~T065, T079~T080 등)

---

## 병렬 실행 예시: User Story 1

```bash
# US1 모델들을 동시에 생성:
Task T032: TravelPlan 모델 생성
Task T033: DailyItinerary 모델 생성
Task T034: Place 모델 생성
Task T035: ItineraryPlace 모델 생성
Task T036: Route 모델 생성

# US1 스키마들을 동시에 생성:
Task T039: TravelPlan 스키마
Task T040: Place 스키마
Task T041: DailyItinerary 스키마

# US1 프론트엔드 컴포넌트들을 동시에 생성:
Task T063: 일일 타임라인 컴포넌트
Task T064: 장소 카드 컴포넌트
Task T065: 예산 요약 컴포넌트
```

---

## 구현 전략

### MVP 우선 (User Story 1만)

1. Phase 1 완료: 프로젝트 초기 설정
2. Phase 2 완료: 기반 인프라 (중요 - 모든 스토리 차단)
3. Phase 3 완료: User Story 1
4. **중단 및 검증**: User Story 1을 독립적으로 테스트
5. 준비되면 배포/데모

### 점진적 배포

1. 프로젝트 초기 설정 + 기반 인프라 완료 → 기반 준비
2. User Story 1 추가 → 독립 테스트 → 배포/데모 (MVP!)
3. User Story 2 추가 → 독립 테스트 → 배포/데모
4. User Story 3 추가 → 독립 테스트 → 배포/데모
5. User Story 4 추가 → 독립 테스트 → 배포/데모
6. User Story 5 추가 → 독립 테스트 → 배포/데모
7. 각 스토리가 이전 스토리를 깨뜨리지 않고 가치를 추가

### 병렬 팀 전략

여러 개발자가 있는 경우:

1. 팀이 함께 프로젝트 초기 설정 + 기반 인프라 완료
2. 기반 인프라 완료 후:
   - 개발자 A: User Story 1
   - 개발자 B: User Story 2
   - 개발자 C: User Story 3
3. 스토리들이 독립적으로 완료되고 통합됨

---

## 작업 통계

- **총 작업 수**: 144개
- **User Story별 작업 수**:
  - Phase 1 (프로젝트 초기 설정): 8개
  - Phase 2 (기반 인프라): 23개
  - User Story 1 (P1 - AI 여행 일정 생성): 38개
  - User Story 2 (P2 - 지도 시각화): 14개
  - User Story 3 (P2 - PDF 생성): 11개
  - User Story 4 (P3 - 예약 링크): 17개
  - User Story 5 (P3 - 선호도 학습): 11개
  - Phase 8 (성능 최적화 및 마무리): 22개

- **병렬 실행 가능 작업**: 약 60개 (전체의 42%)
- **MVP 범위 (US1만)**: Phase 1 + Phase 2 + Phase 3 = 69개 작업

---

## 주의사항

- **[P]** 작업 = 다른 파일, 의존성 없음
- **[Story]** 레이블은 작업을 특정 사용자 스토리에 매핑하여 추적성 제공
- 각 사용자 스토리는 독립적으로 완료 및 테스트 가능해야 함
- 각 작업 또는 논리적 그룹 완료 후 커밋
- 체크포인트에서 멈춰 스토리를 독립적으로 검증
- 피해야 할 것: 모호한 작업, 동일 파일 충돌, 독립성을 깨는 스토리 간 의존성

---

**작업 목록 생성 완료** ✅

다음 단계: `/speckit.implement` 명령으로 tasks.md의 작업들을 순차적으로 실행
