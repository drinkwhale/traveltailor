# 연구: AI TripSmith - 개인 맞춤형 여행 설계 서비스

**날짜**: 2025-10-19
**단계**: 0 (개요 및 연구)
**상태**: 완료

## 개요

이 문서는 AI TripSmith 여행 계획 서비스를 위한 기술 결정, 외부 API 통합 및 모범 사례에 대한 연구 결과를 통합합니다.

---

## 1. AI 여행 계획 아키텍처

### 결정: LangChain + OpenAI GPT-4

**근거**:
- **LangChain**은 메모리, 컨텍스트 관리 및 체인 오케스트레이션을 갖춘 AI 애플리케이션 구축을 위한 강력한 프레임워크를 제공합니다
- **GPT-4**는 다단계 의사결정(예산 최적화, 경로 계획, 선호도 매칭)이 필요한 복잡한 여행 계획을 위한 우수한 추론 능력을 제공합니다
- LangChain의 메모리 모듈은 세션 간 사용자 선호도 학습을 가능하게 합니다
- 구조화된 출력(JSON)에 대한 기본 지원으로 일관된 API 응답을 보장합니다

**고려된 대안**:
- **Claude 3 Opus**: 우수한 추론 능력이지만 비용이 높고 생태계 지원이 적음
- **오픈소스 LLM(LLaMA 3, Mixtral)**: 비용은 낮지만 자체 호스팅 인프라가 필요하고 복잡한 계획에 대한 신뢰성이 낮음
- **커스텀 ML 모델**: 광범위한 학습 데이터와 더 긴 개발 시간이 필요함

**구현 접근법**:
- 세션 기반 컨텍스트를 위해 LangChain의 `ConversationBufferMemory` 사용
- 일관된 JSON 응답을 보장하기 위해 `StructuredOutputParser` 사용
- API 속도 제한을 위한 지수 백오프가 있는 재시도 로직 구현
- API 비용을 줄이기 위해 일반적인 쿼리(예: 인기 목적지) 캐싱

---

## 2. 외부 데이터 소스 및 API

### 2.1 장소 및 관심 지점

**결정**: Google Places API + TripAdvisor Content API

**근거**:
- Google Places는 평점, 사진, 영업 시간을 포함한 포괄적인 글로벌 커버리지를 제공합니다
- TripAdvisor는 상세한 리뷰와 여행자 인사이트를 제공합니다
- 결합된 접근 방식은 풍부한 장소 정보를 보장합니다

**고려된 대안**:
- Foursquare API: 좋은 커버리지이지만 리뷰가 덜 상세함
- Yelp API: 레스토랑에 강하지만 국제 커버리지가 제한적임

**통합 세부사항**:
- Google Places API: Nearby Search, Place Details, Place Photos
- 속도 제한: 1000 요청/일 (무료 티어), 필요에 따라 업그레이드 가능
- 캐싱 전략: API 호출을 최소화하기 위해 장소 세부정보를 24시간 동안 캐싱

### 2.2 항공편 검색

**결정**: Skyscanner Flight Search API

**근거**:
- 여러 항공사의 포괄적인 항공편 집계
- 검색 및 예약 링크 모두 제공
- 수수료 기반 수익을 위한 제휴 프로그램

**고려된 대안**:
- Amadeus API: 엔터프라이즈급이지만 복잡한 가격 정책
- Kiwi.com API: 좋은 커버리지이지만 문서화가 덜 신뢰할 수 있음

**통합 세부사항**:
- 가격 견적을 위해 "Browse Quotes" 엔드포인트 사용
- 실제 예약을 위해 Skyscanner로 딥링크
- 수익 귀속을 위한 제휴 추적

### 2.3 숙박 검색

**결정**: Booking.com 제휴 파트너 프로그램 + Agoda API

**근거**:
- Booking.com은 가장 큰 글로벌 인벤토리를 보유
- Agoda는 아시아-태평양 지역에서 강력한 커버리지 제공
- 둘 다 제휴 수수료 제공 (4-6%)

**고려된 대안**:
- Airbnb API: 신규 파트너에 대한 API 액세스 제한
- Expedia Rapid API: 좋은 커버리지이지만 복잡한 통합

**통합 세부사항**:
- 추적 매개변수가 있는 제휴 딥링크 사용
- 1시간 동안 가용성 확인 캐싱
- API 실패 시 직접 검색으로 폴백

### 2.4 지도 및 경로 시각화

**결정**: Mapbox GL JS

**근거**:
- 현대적이고 성능이 우수한 지도 렌더링
- 우수한 모바일 지원
- 브랜드 일관성을 위한 사용자 정의 가능한 스타일링
- 관대한 무료 티어 (월 50,000회 로드)

**고려된 대안**:
- Google Maps JavaScript API: 더 비싸고 사용자 정의가 덜 가능함
- Leaflet + OpenStreetMap: 무료이지만 더 많은 설정이 필요함

**통합 세부사항**:
- 경로 계산을 위해 Directions API 사용
- 경유지 순서로 경로 최적화
- 외부 지도 앱을 위해 경로를 GeoJSON으로 내보내기

### 2.5 경로 내보내기 (카카오맵 / Google Maps)

**결정**: URL 스키마를 사용한 딥링킹

**근거**:
- API 통합이 필요하지 않음
- 직접적인 사용자 경험
- 모바일 및 데스크톱 모두에서 작동

**구현**:
- 카카오맵: `https://map.kakao.com/link/map/[name],[lat],[lng]`
- Google Maps: `https://www.google.com/maps/dir/?api=1&waypoints=[coordinates]`
- 사용자 플랫폼(iOS/Android) 감지 및 적절한 링크 제공

---

## 3. PDF 생성

### 결정: Puppeteer (Node.js)

**근거**:
- HTML/CSS 템플릿에서 PDF 생성
- 스타일링 및 브랜딩에 대한 완전한 제어
- 복잡한 레이아웃(지도, 타임라인, 표) 렌더링 가능
- 좋은 문서화가 있는 성숙한 생태계

**고려된 대안**:
- ReportLab (Python): 더 복잡한 API, 덜 유연한 스타일링
- jsPDF: 복잡한 문서에 대한 제한된 레이아웃 기능
- Prince XML: 상용 라이선스 필요

**구현 세부사항**:
- 스타일링을 위해 Tailwind CSS를 사용한 HTML 템플릿 생성
- PDF 렌더링을 위해 Puppeteer 헤드리스 Chrome 사용
- PDF에 포함할 정적 지도 이미지(Mapbox Static API) 생성
- 목표 생성 시간: <10초
- 브라우저 인스턴스 풀을 사전 워밍하여 최적화

---

## 4. 데이터베이스 및 스토리지

### 결정: Supabase (PostgreSQL + 인증 + 스토리지)

**근거**:
- 실시간 기능을 갖춘 관리형 PostgreSQL
- 내장 인증 (이메일, OAuth)
- PDF용 파일 스토리지
- MVP에 적합한 무료 티어
- 자체 호스팅 Postgres로의 쉬운 마이그레이션 경로

**고려된 대안**:
- Firebase: 빠른 프로토타이핑에 좋지만 SQL 기능이 제한적임
- AWS RDS + Cognito: 더 많은 제어이지만 더 높은 복잡성
- 자체 호스팅 PostgreSQL: DevOps 오버헤드가 필요함

**스키마 설계**:
```sql
-- 스펙의 핵심 엔티티
users (id, email, created_at, preferences_json)
travel_plans (id, user_id, destination, start_date, end_date, budget, status)
daily_itineraries (id, plan_id, date, day_number)
places (id, name, location, category, details_json)
itinerary_places (id, itinerary_id, place_id, visit_time, duration)
routes (id, from_place_id, to_place_id, mode, duration, distance)
```

---

## 5. 프론트엔드 프레임워크 및 UI

### 결정: Next.js 15 (App Router) + Tailwind CSS + Shadcn UI

**근거**:
- Next.js는 SSR, API 라우트 및 우수한 개발자 경험을 제공합니다
- App Router는 더 나은 코드 구성을 가능하게 합니다
- Tailwind CSS로 빠른 UI 개발
- Shadcn UI는 접근 가능하고 사용자 정의 가능한 컴포넌트를 제공합니다

**고려된 대안**:
- Remix: 좋은 SSR이지만 생태계가 작음
- Vite + React: 빠르지만 더 많은 구성이 필요함
- Nuxt.js (Vue): 좋지만 팀 전문성이 React에 있음

**컴포넌트 아키텍처**:
- 기능 기반 폴더 구조
- 공유 컴포넌트 라이브러리
- API 호출을 위한 커스텀 훅
- 데이터 페칭 및 캐싱을 위한 React Query

---

## 6. 인증 및 권한 부여

### 결정: 이메일 + 소셜 로그인이 있는 Supabase Auth

**근거**:
- Supabase 데이터베이스와 통합됨
- 이메일/비밀번호 및 OAuth(Google, Kakao) 지원
- JWT 기반 인증
- 데이터 보호를 위한 행 수준 보안(RLS)

**구현**:
- MVP용 이메일/비밀번호
- 소셜 로그인을 위한 Google OAuth 추가
- 한국 시장을 위한 Kakao OAuth 고려
- 사용자 데이터 액세스를 제한하기 위해 RLS 정책 사용

---

## 7. AI 프롬프트 엔지니어링 전략

### 결정: 구조화된 출력을 사용한 다단계 프롬프트 체인

**근거**:
- 복잡한 여행 계획은 문제 분해가 필요함
- 구조화된 출력은 신뢰할 수 있는 파싱을 보장함
- 컨텍스트 주입은 개인화를 가능하게 함

**프롬프트 체인 설계**:
1. **선호도 분석**: 입력에서 사용자 의도 추출
2. **예산 할당**: 예산 분할 계산 (숙박, 음식, 활동, 교통)
3. **장소 선택**: 외부 API 쿼리 및 선호도 매치별로 순위 지정
4. **경로 최적화**: 최적 방문 순서 계산
5. **타임라인 생성**: 장소 시간 및 거리를 기반으로 시간대 할당

**예시 프롬프트 구조**:
```
당신은 전문 여행 계획자입니다. 다음 입력을 기반으로:
- 목적지: {destination}
- 기간: {days}일
- 예산: {budget}원
- 여행자 유형: {type}
- 선호사항: {preferences}

다음을 포함하는 JSON 형식의 일일 일정을 생성하세요:
- 권장 숙박 예산
- 오전/오후/저녁 활동
- 레스토랑 제안
- 예상 비용
```

---

## 8. 성능 최적화

### 결정사항:

1. **캐싱 전략**:
   - API 응답 캐싱을 위한 Redis (장소 세부정보, 항공편 가격)
   - 정적 자산 및 생성된 PDF를 위한 CDN
   - 지도 타일을 위한 브라우저 캐싱

2. **데이터베이스 최적화**:
   - 자주 쿼리되는 필드에 인덱스 (user_id, destination, date)
   - 동시 요청 처리를 위한 연결 풀링
   - 분석 쿼리를 위한 읽기 복제본

3. **API 속도 제한**:
   - 외부 API를 위한 요청 큐 구현
   - 사용자 기반 속도 제한 (예: 무료 티어의 경우 하루 10회 계획 생성)
   - API가 속도 제한될 때 우아한 성능 저하

4. **비동기 처리**:
   - PDF 생성을 위한 백그라운드 작업 사용 (Celery 또는 Bull)
   - 실시간 계획 생성 상태를 위한 WebSocket 또는 SSE
   - 버스트 트래픽 처리를 위한 큐 시스템

---

## 9. 오류 처리 및 복원력

### 전략:

1. **회로 차단기 패턴**:
   - 실패하는 외부 API 감지
   - 일시적으로 비활성화하고 캐시된 데이터로 폴백

2. **우아한 성능 저하**:
   - 항공편 API 실패 시: "항공편 검색 일시적으로 사용 불가" 메시지 표시
   - 장소 API 실패 시: 캐시된 인기 목적지 사용
   - AI API 실패 시: 간소화된 템플릿 기반 계획 제공

3. **재시도 로직**:
   - 일시적 실패를 위한 지수 백오프
   - 오류 표시 전 최대 3회 재시도
   - API별로 다른 재시도 전략 (일부는 더 불안정함)

---

## 10. 보안 및 개인정보 보호

### 결정사항:

1. **데이터 암호화**:
   - 저장 시 사용자 선호도 암호화
   - 모든 API 통신에 HTTPS
   - 결제 카드 데이터 저장 금지 (Stripe/Toss 사용)

2. **GDPR 준수**:
   - 사용자 데이터 내보내기 기능
   - 잊혀질 권리 (데이터 삭제)
   - 명확한 개인정보 보호정책 및 동의

3. **API 키 관리**:
   - 환경 변수에 API 키 저장
   - 비밀 관리를 위해 Supabase Vault 사용
   - 주기적으로 키 교체

---

## 11. 배포 및 DevOps

### 결정: Vercel (프론트엔드) + Railway/Render (백엔드)

**근거**:
- Vercel은 Next.js 배포에 최적화됨
- Railway는 간단한 Python/FastAPI 호스팅 제공
- 둘 다 MVP에 적합한 무료 티어 제공
- CI/CD를 위한 GitHub와의 쉬운 통합

**고려된 대안**:
- AWS (EC2 + S3 + CloudFront): 더 많은 제어이지만 더 높은 복잡성
- Heroku: 간단하지만 비쌈
- DigitalOcean App Platform: 좋은 중간 지점

**CI/CD 파이프라인**:
- 자동화된 테스트를 위한 GitHub Actions
- 풀 리퀘스트를 위한 미리보기 배포
- 자동화된 데이터베이스 마이그레이션
- 롤백 기능

---

## 12. 모니터링 및 분석

### 결정: Vercel Analytics + Sentry + PostHog

**근거**:
- 웹 바이탈 및 성능을 위한 Vercel Analytics
- 오류 추적 및 디버깅을 위한 Sentry
- 제품 분석 및 사용자 행동을 위한 PostHog

**추적할 주요 메트릭**:
- AI 생성 성공률
- 평균 생성 시간
- 외부 API 실패율
- PDF 다운로드율
- 사용자 유지 및 이탈
- 가장 인기 있는 목적지

---

## 13. 로컬라이제이션 및 i18n

### 결정: 국제화를 위한 next-intl

**근거**:
- Next.js App Router와 잘 통합됨
- 한국어 및 영어 지원
- 새로운 언어 추가 용이

**초기 언어**:
- 한국어 (기본)
- 영어 (확장을 위한 보조)

**로컬라이제이션 요소**:
- UI 텍스트 및 레이블
- 오류 메시지
- PDF 템플릿
- AI 프롬프트 (더 나은 로컬 추천을 위해)

---

## 주요 기술 결정 요약

| 영역 | 기술 선택 | 주요 이유 |
|------|-------------------|----------------|
| AI 엔진 | LangChain + GPT-4 | 최고의 추론, 생태계 지원 |
| 프론트엔드 | Next.js 15 + Tailwind | 현대적, 성능, 훌륭한 개발자 경험 |
| 백엔드 | FastAPI + Python | 비동기 지원, AI 생태계 |
| 데이터베이스 | Supabase (PostgreSQL) | 관리형, 인증 포함, 무료 티어 |
| 지도 | Mapbox GL JS | 사용자 정의 가능, 성능 |
| PDF | Puppeteer | 완전한 제어, HTML/CSS 템플릿 |
| 장소 데이터 | Google Places + TripAdvisor | 최고의 커버리지 및 품질 |
| 항공편 | Skyscanner API | 제휴 프로그램, 좋은 UX |
| 호스팅 | Vercel + Railway | 쉬운 배포, 무료 티어 |
| 모니터링 | Sentry + PostHog | 오류 추적 + 분석 |

---

## 다음 단계 (1단계)

1. `data-model.md`에서 상세한 데이터 모델 정의
2. `contracts/api-spec.yaml`에서 REST API용 OpenAPI 사양 생성
3. `quickstart.md`에서 개발자 빠른 시작 가이드 작성
4. 기술 스택으로 에이전트 컨텍스트 업데이트

---

**연구 완료** ✅
