# 데이터 모델: AI TravelTailor

**날짜**: 2025-10-19
**단계**: 1 (설계 및 계약)
**데이터베이스**: PostgreSQL (Supabase 사용)

## 개요

이 문서는 AI TravelTailor 여행 계획 서비스를 위한 데이터 엔티티, 관계 및 유효성 검사 규칙을 정의합니다. 이 모델은 [spec.md](./spec.md)의 핵심 엔티티 섹션에서 도출되었습니다.

---

## 엔티티 관계 다이어그램

```
User (1) ──────< (M) TravelPlan
                      │
                      └──< (M) DailyItinerary
                                │
                                ├──< (M) ItineraryPlace ──> (1) Place
                                └──< (M) Route

User (1) ──────< (1) UserPreference

TravelPlan (1) ──────< (M) FlightOption
TravelPlan (1) ──────< (M) AccommodationOption
```

---

## 핵심 엔티티

### 1. User (사용자)

**설명**: TravelTailor 서비스의 등록된 사용자를 나타냅니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 사용자 식별자 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 사용자 이메일 주소 |
| full_name | VARCHAR(100) | NULLABLE | 사용자 전체 이름 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 계정 생성 타임스탬프 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 마지막 업데이트 타임스탬프 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 계정 상태 |
| subscription_tier | ENUM | NOT NULL, DEFAULT 'free' | 구독 레벨 (free, premium) |

**유효성 검사 규칙**:
- 이메일은 유효한 형식이어야 함
- 이메일은 고유해야 함
- 구독 티어: ['free', 'premium']

**인덱스**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

---

### 2. UserPreference (사용자 선호도)

**설명**: 개인화된 추천을 위한 사용자 여행 선호도를 저장합니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 선호도 식별자 |
| user_id | UUID | FOREIGN KEY, NOT NULL | User 참조 |
| default_budget_min | INTEGER | NULLABLE | 선호하는 최소 예산 (원) |
| default_budget_max | INTEGER | NULLABLE | 선호하는 최대 예산 (원) |
| preferred_traveler_types | TEXT[] | NULLABLE | 선호 여행 유형 배열 ['couple', 'family', 'solo', 'friends'] |
| preferred_interests | TEXT[] | NULLABLE | 관심사 배열 ['food', 'sightseeing', 'relaxation', 'culture', 'adventure'] |
| avoided_activities | TEXT[] | NULLABLE | 피해야 할 활동 |
| dietary_restrictions | TEXT[] | NULLABLE | 식이 선호도 ['vegetarian', 'vegan', 'halal', 'kosher'] |
| mobility_considerations | TEXT | NULLABLE | 접근성 요구사항 |
| preferred_accommodation_type | TEXT[] | NULLABLE | 선호 숙박 유형 ['hotel', 'hostel', 'resort', 'guesthouse', 'airbnb'] |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 마지막 업데이트 타임스탬프 |

**유효성 검사 규칙**:
- 두 값이 모두 설정된 경우 최소 예산이 최대 예산보다 작아야 함
- 여행자 유형은 허용된 enum에서 선택해야 함
- 관심사는 허용된 enum에서 선택해야 함

**인덱스**:
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `user_id`

---

### 3. TravelPlan (여행 계획)

**설명**: AI가 생성한 완전한 여행 일정을 나타냅니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 계획 식별자 |
| user_id | UUID | FOREIGN KEY, NOT NULL | User 참조 |
| title | VARCHAR(200) | NOT NULL | 사용자 정의 또는 자동 생성된 제목 |
| destination | VARCHAR(100) | NOT NULL | 주요 목적지 (도시/지역) |
| country | VARCHAR(100) | NOT NULL | 목적지 국가 |
| start_date | DATE | NOT NULL | 여행 시작일 |
| end_date | DATE | NOT NULL | 여행 종료일 |
| total_days | INTEGER | NOT NULL | 계산: end_date - start_date + 1 |
| total_nights | INTEGER | NOT NULL | 계산: total_days - 1 |
| budget_total | INTEGER | NOT NULL | 총 예산 (원) |
| budget_allocated | INTEGER | NULLABLE | AI가 할당한 실제 예산 |
| budget_breakdown | JSONB | NULLABLE | 예산 분류 (숙박, 식사, 활동, 교통) |
| traveler_type | VARCHAR(50) | NOT NULL | 여행 유형 ['couple', 'family', 'solo', 'friends'] |
| traveler_count | INTEGER | NOT NULL, DEFAULT 1 | 여행자 수 |
| preferences | JSONB | NOT NULL | 이 특정 여행에 대한 사용자 선호도 |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'draft' | 계획 상태 ['draft', 'completed', 'archived'] |
| ai_model_version | VARCHAR(50) | NULLABLE | 생성에 사용된 AI 모델 |
| generation_time_seconds | DECIMAL(5,2) | NULLABLE | 계획 생성에 소요된 시간 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 마지막 업데이트 타임스탬프 |

**유효성 검사 규칙**:
- 종료일은 시작일 이후여야 함
- 총 일수는 0보다 커야 함
- 총 예산은 0보다 커야 함
- 여행자 수는 1 이상이어야 함
- 상태는 허용된 enum에서 선택해야 함

**인덱스**:
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `destination`
- INDEX on `created_at` (정렬용)

---

### 4. DailyItinerary (일일 일정)

**설명**: 여행 계획 내의 특정 날짜에 대한 계획을 나타냅니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 일정 식별자 |
| travel_plan_id | UUID | FOREIGN KEY, NOT NULL | TravelPlan 참조 |
| date | DATE | NOT NULL | 특정 날짜 |
| day_number | INTEGER | NOT NULL | 일자 순서 (1, 2, 3...) |
| theme | VARCHAR(100) | NULLABLE | 일일 테마 (예: "문화 탐방", "음식 투어") |
| notes | TEXT | NULLABLE | 사용자 메모 또는 AI 생성 하이라이트 |
| weather_forecast | JSONB | NULLABLE | 날씨 데이터 (사용 가능한 경우) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 마지막 업데이트 타임스탬프 |

**유효성 검사 규칙**:
- 날짜는 travel_plan의 start_date와 end_date 사이여야 함
- 일자 번호는 순차적이어야 함
- UNIQUE 제약조건 on (travel_plan_id, day_number)
- UNIQUE 제약조건 on (travel_plan_id, date)

**인덱스**:
- PRIMARY KEY on `id`
- INDEX on `travel_plan_id`
- UNIQUE INDEX on `(travel_plan_id, day_number)`

---

### 5. Place (장소)

**설명**: 위치/장소(숙박시설, 레스토랑, 관광지 등)를 나타냅니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 장소 식별자 |
| external_id | VARCHAR(100) | NULLABLE | 외부 API의 ID (Google Places 등) |
| external_source | VARCHAR(50) | NULLABLE | 데이터 출처 ['google_places', 'tripadvisor', 'custom'] |
| name | VARCHAR(200) | NOT NULL | 장소 이름 |
| category | VARCHAR(50) | NOT NULL | 카테고리 ['accommodation', 'restaurant', 'cafe', 'attraction', 'shopping', 'transport'] |
| subcategory | VARCHAR(100) | NULLABLE | 더 구체적인 유형 (예: '박물관', '사원', '이탈리안 레스토랑') |
| address | TEXT | NULLABLE | 전체 주소 |
| city | VARCHAR(100) | NULLABLE | 도시 이름 |
| country | VARCHAR(100) | NULLABLE | 국가 이름 |
| latitude | DECIMAL(10,8) | NOT NULL | GPS 위도 |
| longitude | DECIMAL(11,8) | NOT NULL | GPS 경도 |
| rating | DECIMAL(2,1) | NULLABLE | 평균 평점 (0.0-5.0) |
| price_level | INTEGER | NULLABLE | 가격 수준 (1-4, Google Places 기준) |
| phone | VARCHAR(50) | NULLABLE | 연락 전화번호 |
| website | TEXT | NULLABLE | 웹사이트 URL |
| opening_hours | JSONB | NULLABLE | 운영 시간 |
| photos | TEXT[] | NULLABLE | 사진 URL 배열 |
| description | TEXT | NULLABLE | 장소 설명 |
| tags | TEXT[] | NULLABLE | 검색/필터링용 태그 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 마지막 업데이트 타임스탬프 |

**유효성 검사 규칙**:
- 카테고리는 허용된 enum에서 선택해야 함
- 위도는 -90과 90 사이여야 함
- 경도는 -180과 180 사이여야 함
- 평점은 0과 5 사이여야 함
- 가격 수준은 1과 4 사이여야 함

**인덱스**:
- PRIMARY KEY on `id`
- INDEX on `external_id`
- INDEX on `city`
- INDEX on `category`
- GIS INDEX on `(latitude, longitude)` (근접 검색용)

---

### 6. ItineraryPlace (일정 장소)

**설명**: 장소를 일일 일정에 연결하며 시간 및 방문 세부정보를 포함합니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 레코드 식별자 |
| daily_itinerary_id | UUID | FOREIGN KEY, NOT NULL | DailyItinerary 참조 |
| place_id | UUID | FOREIGN KEY, NOT NULL | Place 참조 |
| visit_order | INTEGER | NOT NULL | 일일 순서 (1, 2, 3...) |
| visit_time | TIME | NULLABLE | 예정된 도착 시간 |
| duration_minutes | INTEGER | NULLABLE | 예상 체류 시간 |
| visit_type | VARCHAR(50) | NOT NULL | 유형 ['overnight', 'meal', 'activity', 'transit'] |
| estimated_cost | INTEGER | NULLABLE | 1인당 예상 비용 (원) |
| ai_recommendation_reason | TEXT | NULLABLE | AI가 이 장소를 추천한 이유 |
| user_notes | TEXT | NULLABLE | 사용자 추가 메모 |
| is_confirmed | BOOLEAN | NOT NULL, DEFAULT TRUE | 사용자가 이 장소를 확인했는지 여부 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 마지막 업데이트 타임스탬프 |

**유효성 검사 규칙**:
- 방문 순서는 하루 내에서 순차적이어야 함
- 설정된 경우 체류 시간은 0보다 커야 함
- 방문 유형은 허용된 enum에서 선택해야 함

**인덱스**:
- PRIMARY KEY on `id`
- INDEX on `daily_itinerary_id`
- INDEX on `place_id`
- INDEX on `(daily_itinerary_id, visit_order)` (정렬용)

---

### 7. Route (경로)

**설명**: 두 장소 간의 이동(도보, 운전, 대중교통)을 나타냅니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 경로 식별자 |
| daily_itinerary_id | UUID | FOREIGN KEY, NOT NULL | DailyItinerary 참조 |
| from_place_id | UUID | FOREIGN KEY, NOT NULL | 출발 장소 |
| to_place_id | UUID | FOREIGN KEY, NOT NULL | 도착 장소 |
| from_order | INTEGER | NOT NULL | from_place의 방문 순서 |
| to_order | INTEGER | NOT NULL | to_place의 방문 순서 |
| transport_mode | VARCHAR(50) | NOT NULL | 이동 수단 ['walking', 'driving', 'public_transit', 'taxi', 'bicycle'] |
| distance_meters | INTEGER | NULLABLE | 미터 단위 거리 |
| duration_minutes | INTEGER | NULLABLE | 예상 이동 시간 |
| estimated_cost | INTEGER | NULLABLE | 예상 교통 비용 (원) |
| route_polyline | TEXT | NULLABLE | 지도 표시용 인코딩된 폴리라인 |
| instructions | JSONB | NULLABLE | 턴바이턴 길안내 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 마지막 업데이트 타임스탬프 |

**유효성 검사 규칙**:
- from_place_id != to_place_id
- to_order는 from_order보다 커야 함
- 이동 수단은 허용된 enum에서 선택해야 함
- 설정된 경우 소요 시간은 0보다 커야 함

**인덱스**:
- PRIMARY KEY on `id`
- INDEX on `daily_itinerary_id`
- INDEX on `from_place_id`
- INDEX on `to_place_id`

---

### 8. FlightOption (항공편 옵션)

**설명**: 여행 계획에 대한 항공편 추천을 나타냅니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 옵션 식별자 |
| travel_plan_id | UUID | FOREIGN KEY, NOT NULL | TravelPlan 참조 |
| flight_type | VARCHAR(50) | NOT NULL | 유형 ['outbound', 'return'] |
| airline | VARCHAR(100) | NOT NULL | 항공사 이름 |
| flight_number | VARCHAR(20) | NULLABLE | 항공편 번호 |
| departure_airport | VARCHAR(10) | NOT NULL | IATA 공항 코드 |
| arrival_airport | VARCHAR(10) | NOT NULL | IATA 공항 코드 |
| departure_time | TIMESTAMP | NOT NULL | 출발 날짜/시간 |
| arrival_time | TIMESTAMP | NOT NULL | 도착 날짜/시간 |
| duration_minutes | INTEGER | NOT NULL | 비행 시간 |
| stops | INTEGER | NOT NULL, DEFAULT 0 | 경유 횟수 |
| price_krw | INTEGER | NOT NULL | 원 단위 가격 |
| booking_url | TEXT | NOT NULL | 예약용 제휴 링크 |
| external_reference | VARCHAR(100) | NULLABLE | API의 참조 ID |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| expires_at | TIMESTAMP | NULLABLE | 가격/옵션 만료 시점 |

**유효성 검사 규칙**:
- 항공편 유형은 ['outbound', 'return']이어야 함
- 도착 시간은 출발 시간 이후여야 함
- 소요 시간은 0보다 커야 함
- 가격은 0보다 커야 함
- 경유 횟수는 0 이상이어야 함

**인덱스**:
- PRIMARY KEY on `id`
- INDEX on `travel_plan_id`
- INDEX on `departure_time`

---

### 9. AccommodationOption (숙박 옵션)

**설명**: 여행 계획에 대한 숙박 추천을 나타냅니다.

**필드**:

| 필드 | 타입 | 제약조건 | 설명 |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | 고유 옵션 식별자 |
| travel_plan_id | UUID | FOREIGN KEY, NOT NULL | TravelPlan 참조 |
| place_id | UUID | FOREIGN KEY, NULLABLE | Place 참조 (저장된 경우) |
| name | VARCHAR(200) | NOT NULL | 호텔/숙박시설 이름 |
| type | VARCHAR(50) | NOT NULL | 유형 ['hotel', 'hostel', 'resort', 'guesthouse', 'vacation_rental'] |
| address | TEXT | NOT NULL | 전체 주소 |
| latitude | DECIMAL(10,8) | NOT NULL | GPS 위도 |
| longitude | DECIMAL(11,8) | NOT NULL | GPS 경도 |
| rating | DECIMAL(2,1) | NULLABLE | 평균 평점 (0.0-5.0) |
| review_count | INTEGER | NULLABLE | 리뷰 수 |
| price_per_night_krw | INTEGER | NOT NULL | 1박 가격 |
| total_price_krw | INTEGER | NOT NULL | 총 숙박 가격 |
| check_in_date | DATE | NOT NULL | 체크인 날짜 |
| check_out_date | DATE | NOT NULL | 체크아웃 날짜 |
| nights | INTEGER | NOT NULL | 숙박 일수 |
| amenities | TEXT[] | NULLABLE | 편의시설 목록 |
| photos | TEXT[] | NULLABLE | 사진 URL |
| booking_url | TEXT | NOT NULL | 제휴 예약 링크 |
| external_reference | VARCHAR(100) | NULLABLE | 예약 API의 참조 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 타임스탬프 |
| expires_at | TIMESTAMP | NULLABLE | 가격 만료 |

**유효성 검사 규칙**:
- 유형은 허용된 enum에서 선택해야 함
- 체크아웃 날짜는 체크인 날짜 이후여야 함
- 숙박 일수는 (check_out - check_in)과 일치해야 함
- 총 가격은 (price_per_night * nights)와 같아야 함
- 평점은 0과 5 사이여야 함

**인덱스**:
- PRIMARY KEY on `id`
- INDEX on `travel_plan_id`
- INDEX on `check_in_date`

---

## 열거형 및 상수

### 구독 티어
- `free`: 무료 티어 (제한된 계획 생성)
- `premium`: 프리미엄 구독 (무제한 계획)

### 여행자 유형
- `couple`: 로맨틱/커플 여행
- `family`: 어린이를 동반한 가족
- `solo`: 혼자 여행
- `friends`: 친구 그룹

### 관심사/선호도
- `food`: 요리 체험, 레스토랑, 음식 투어
- `sightseeing`: 관광 명소, 랜드마크
- `relaxation`: 스파, 해변, 조용한 장소
- `culture`: 박물관, 사원, 문화 체험
- `adventure`: 하이킹, 스포츠, 야외 활동
- `shopping`: 시장, 쇼핑몰, 부티크
- `nightlife`: 바, 클럽, 엔터테인먼트

### 장소 카테고리
- `accommodation`: 호텔, 호스텔 등
- `restaurant`: 식당
- `cafe`: 커피숍, 찻집
- `attraction`: 관광지, 랜드마크
- `shopping`: 상점, 시장
- `transport`: 환승 허브, 역

### 이동 수단
- `walking`: 도보
- `driving`: 개인 차량 또는 렌터카
- `public_transit`: 버스, 지하철, 기차
- `taxi`: 택시 또는 차량 호출
- `bicycle`: 자전거 또는 스쿠터

### 계획 상태
- `draft`: 생성 중 또는 편집 중
- `completed`: 완료되어 준비됨
- `archived`: 참조용으로 저장됨

---

## 데이터 관계

### 일대다 관계

1. **User → TravelPlan**: 한 사용자는 여러 여행 계획을 생성할 수 있음
2. **User → UserPreference**: 한 사용자는 하나의 선호도 프로필을 가짐 (1:1)
3. **TravelPlan → DailyItinerary**: 한 계획은 여러 일일 일정을 가짐
4. **TravelPlan → FlightOption**: 한 계획은 여러 항공편 옵션을 가짐
5. **TravelPlan → AccommodationOption**: 한 계획은 여러 숙박 옵션을 가짐
6. **DailyItinerary → ItineraryPlace**: 하루는 여러 방문 장소를 가짐
7. **DailyItinerary → Route**: 하루는 장소 간 여러 경로를 가짐

### 다대일 관계

1. **ItineraryPlace → Place**: 여러 일정 항목이 같은 장소를 참조할 수 있음
2. **Route → Place**: 여러 경로가 같은 장소에서 시작/종료될 수 있음

---

## 데이터베이스 제약조건

### 참조 무결성
- 모든 외래 키는 여행 계획 삭제 시 `ON DELETE CASCADE` 적용
- 사용자 삭제 시 `ON DELETE SET NULL` (익명화된 데이터 보존)

### 체크 제약조건
```sql
-- TravelPlan
ALTER TABLE travel_plans ADD CONSTRAINT check_dates
  CHECK (end_date > start_date);

ALTER TABLE travel_plans ADD CONSTRAINT check_budget
  CHECK (budget_total > 0);

-- Route
ALTER TABLE routes ADD CONSTRAINT check_different_places
  CHECK (from_place_id != to_place_id);

-- ItineraryPlace
ALTER TABLE itinerary_places ADD CONSTRAINT check_duration
  CHECK (duration_minutes IS NULL OR duration_minutes > 0);
```

---

## 데이터 마이그레이션 전략

### 초기 스키마
1. 기본 테이블 생성 (User, UserPreference, Place)
2. 여행 계획 테이블 생성 (TravelPlan, DailyItinerary)
3. 관계 테이블 생성 (ItineraryPlace, Route)
4. 추천 테이블 생성 (FlightOption, AccommodationOption)

### 시드 데이터
- 인기 목적지 및 랜드마크
- 공통 장소 (공항, 역)
- 기본 사용자 선호도 템플릿

---

## 성능 고려사항

### 인덱싱 전략
- 모든 외래 키에 인덱스
- 일반적인 쿼리 패턴에 대한 복합 인덱스
- 위치 기반 쿼리를 위한 GIS 인덱스

### 데이터 보관
- 오래된 여행 계획(>1년)을 별도 테이블로 보관
- 사용자 데이터에 대한 소프트 삭제 (GDPR 준수)

### 캐싱 전략
- 인기 장소 데이터 캐싱 (Redis, 24시간 TTL)
- 사용자 선호도 캐싱 (인메모리, 세션 기반)
- 일반적인 목적지 쿼리 구체화

---

**데이터 모델 완료** ✅
