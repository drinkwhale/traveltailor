# Shared 개발 가이드라인

AI TravelTailor 공유 타입 - Frontend와 Backend 간 공유되는 TypeScript 타입 정의

최종 업데이트: 2025-10-23

## 모듈 개요
Frontend(TypeScript)와 Backend(Python)가 API를 통해 통신할 때 사용하는 공통 데이터 구조를 TypeScript 타입으로 정의합니다. 이를 통해 타입 안정성을 보장하고, API 계약을 명시적으로 문서화합니다.

## 기술 스택
- **언어**: TypeScript 5.6.3
- **패키지 관리**: npm (독립 패키지)
- **배포**: npm private registry 또는 로컬 경로 참조

## 디렉토리 구조

```
shared/
├── types/
│   ├── common.ts             # 공통 유틸리티 타입 (Pagination, ApiResponse 등)
│   ├── enums.ts              # Enum 타입 (TripStatus, PlaceType, PreferenceCategory 등)
│   ├── travel-plan.ts        # 여행 일정 관련 타입 (Trip, Itinerary, Place 등)
│   ├── preferences.ts        # 사용자 선호도 타입 (Preferences, TravelStyle 등)
│   ├── recommendations.ts    # 추천 시스템 타입 (Recommendation, Score 등)
│   ├── map.ts                # 지도 관련 타입 (Coordinates, Route, Marker 등)
│   ├── pdf.ts                # PDF 생성 타입 (PdfOptions, PdfMetadata 등)
│   ├── index.ts              # 전체 타입 export
│   └── package.json          # 타입 패키지 메타데이터
│
└── README.md                 # 공유 타입 사용 가이드
```

## 핵심 타입 설명

### 공통 타입 (common.ts)

#### ApiResponse
API 응답 표준 래퍼. 모든 API 엔드포인트는 이 형식을 따릅니다.

```typescript
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: ResponseMetadata;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ResponseMetadata {
  requestId: string;
  timestamp: string;
  version: string;
}
```

**사용 예시**:
```typescript
// Backend (Python)
{
  "success": true,
  "data": { "id": "123", "destination": "도쿄" },
  "meta": { "requestId": "req-abc", "timestamp": "2025-10-23T12:00:00Z", "version": "v1" }
}

// Frontend (TypeScript)
const response: ApiResponse<Trip> = await api.get('/v1/trips/123');
if (response.success && response.data) {
  console.log(response.data.destination); // "도쿄"
}
```

#### Pagination
페이지네이션 메타데이터 및 요청 파라미터.

```typescript
export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginationMeta {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: PaginationMeta;
}
```

**사용 예시**:
```typescript
// Frontend
const params: PaginationParams = { page: 1, pageSize: 10, sortBy: 'createdAt', sortOrder: 'desc' };
const response: PaginatedResponse<Trip> = await api.get('/v1/trips', { params });
console.log(response.data); // Trip[]
console.log(response.pagination); // { currentPage: 1, totalPages: 5, totalItems: 50, itemsPerPage: 10 }
```

### Enum 타입 (enums.ts)

#### TripStatus
여행 일정 상태.

```typescript
export enum TripStatus {
  DRAFT = 'draft',              // 초안 (AI 생성 중)
  PENDING = 'pending',          // 대기 중 (사용자 검토 대기)
  CONFIRMED = 'confirmed',      // 확정 (사용자 승인 완료)
  IN_PROGRESS = 'in_progress',  // 진행 중 (여행 중)
  COMPLETED = 'completed',      // 완료 (여행 종료)
  CANCELLED = 'cancelled',      // 취소
}
```

#### PlaceType
장소 유형.

```typescript
export enum PlaceType {
  ATTRACTION = 'attraction',    // 관광지
  RESTAURANT = 'restaurant',    // 식당
  ACCOMMODATION = 'accommodation', // 숙소
  CAFE = 'cafe',                // 카페
  SHOPPING = 'shopping',        // 쇼핑
  NIGHTLIFE = 'nightlife',      // 나이트라이프
  TRANSPORTATION = 'transportation', // 교통
  OTHER = 'other',              // 기타
}
```

#### PreferenceCategory
사용자 선호도 카테고리.

```typescript
export enum PreferenceCategory {
  TRAVEL_STYLE = 'travel_style',      // 여행 스타일 (예: 여유로운, 빡빡한)
  ACTIVITY_TYPE = 'activity_type',    // 활동 유형 (예: 문화, 자연, 맛집)
  BUDGET_RANGE = 'budget_range',      // 예산 범위 (예: 저렴, 중간, 고급)
  COMPANION_TYPE = 'companion_type',  // 동행자 유형 (예: 혼자, 커플, 가족, 친구)
  ACCOMMODATION_STYLE = 'accommodation_style', // 숙소 스타일 (예: 호텔, 게스트하우스, 에어비앤비)
}
```

### 여행 일정 타입 (travel-plan.ts)

#### Trip
여행 일정 메타데이터.

```typescript
export interface Trip {
  id: string;
  userId: string;
  destination: string;
  startDate: string; // ISO 8601 format
  endDate: string;   // ISO 8601 format
  budget: number;    // 총 예산 (원화)
  status: TripStatus;
  preferences: Preferences;
  itinerary: Itinerary;
  createdAt: string;
  updatedAt: string;
}
```

#### Itinerary
일정표 (날짜별 일정 항목).

```typescript
export interface Itinerary {
  days: DayPlan[];
  totalDistance: number; // 총 이동 거리 (km)
  totalDuration: number; // 총 소요 시간 (분)
  estimatedCost: number; // 예상 총 비용 (원화)
}

export interface DayPlan {
  date: string; // ISO 8601 format
  items: ItineraryItem[];
}

export interface ItineraryItem {
  id: string;
  type: PlaceType;
  place: Place;
  startTime: string; // HH:mm format (예: "09:00")
  endTime: string;   // HH:mm format (예: "11:00")
  duration: number;  // 체류 시간 (분)
  transportToNext?: Transport; // 다음 장소로의 이동 정보
  notes?: string;
  estimatedCost: number; // 예상 비용 (원화)
}
```

#### Place
장소 정보.

```typescript
export interface Place {
  id: string;
  name: string;
  type: PlaceType;
  address: string;
  coordinates: Coordinates;
  rating?: number; // 0.0 ~ 5.0
  priceLevel?: number; // 0 ~ 4 (0: 무료, 4: 매우 비쌈)
  photos?: string[]; // 사진 URL 배열
  description?: string;
  openingHours?: OpeningHours;
  website?: string;
  phone?: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface OpeningHours {
  monday?: TimeRange;
  tuesday?: TimeRange;
  wednesday?: TimeRange;
  thursday?: TimeRange;
  friday?: TimeRange;
  saturday?: TimeRange;
  sunday?: TimeRange;
}

export interface TimeRange {
  open: string;  // HH:mm format
  close: string; // HH:mm format
}
```

#### Transport
장소 간 이동 정보.

```typescript
export interface Transport {
  mode: TransportMode;
  duration: number; // 소요 시간 (분)
  distance: number; // 거리 (km)
  cost?: number;    // 비용 (원화)
  route?: Coordinates[]; // 경로 좌표 배열 (지도 표시용)
}

export enum TransportMode {
  WALK = 'walk',
  DRIVE = 'drive',
  PUBLIC_TRANSIT = 'public_transit',
  TAXI = 'taxi',
  BICYCLE = 'bicycle',
}
```

### 사용자 선호도 타입 (preferences.ts)

#### Preferences
사용자 선호도 전체.

```typescript
export interface Preferences {
  travelStyle: TravelStyle;
  activityTypes: ActivityType[];
  budgetRange: BudgetRange;
  companionType: CompanionType;
  accommodationStyle: AccommodationStyle;
  dietaryRestrictions?: string[]; // 식단 제약 (예: "채식", "할랄")
  accessibility?: AccessibilityNeeds; // 접근성 요구사항
}

export enum TravelStyle {
  RELAXED = 'relaxed',       // 여유로운
  BALANCED = 'balanced',     // 균형잡힌
  PACKED = 'packed',         // 빡빡한
}

export enum ActivityType {
  CULTURE = 'culture',       // 문화 (박물관, 미술관)
  NATURE = 'nature',         // 자연 (산, 바다, 공원)
  FOOD = 'food',             // 맛집
  SHOPPING = 'shopping',     // 쇼핑
  NIGHTLIFE = 'nightlife',   // 나이트라이프
  ADVENTURE = 'adventure',   // 어드벤처 (액티비티)
  RELAXATION = 'relaxation', // 휴식
}

export enum BudgetRange {
  LOW = 'low',       // 저렴 (~50만원)
  MEDIUM = 'medium', // 중간 (50~100만원)
  HIGH = 'high',     // 고급 (100만원~)
}

export enum CompanionType {
  SOLO = 'solo',     // 혼자
  COUPLE = 'couple', // 커플
  FAMILY = 'family', // 가족
  FRIENDS = 'friends', // 친구
}

export enum AccommodationStyle {
  HOTEL = 'hotel',
  HOSTEL = 'hostel',
  GUESTHOUSE = 'guesthouse',
  AIRBNB = 'airbnb',
}

export interface AccessibilityNeeds {
  wheelchairAccessible: boolean;
  elevatorRequired: boolean;
  assistiveDeviceSupport: boolean;
}
```

### 지도 타입 (map.ts)

#### MapViewport
지도 뷰포트 (중심 좌표, 줌 레벨).

```typescript
export interface MapViewport {
  center: Coordinates;
  zoom: number; // 1 ~ 20
}
```

#### Marker
지도 마커.

```typescript
export interface Marker {
  id: string;
  coordinates: Coordinates;
  type: PlaceType;
  label: string;
  icon?: string; // 아이콘 URL
}
```

#### Route
지도 경로.

```typescript
export interface Route {
  coordinates: Coordinates[];
  color?: string; // 경로 색상 (예: "#FF0000")
  width?: number; // 경로 두께 (px)
}
```

### PDF 타입 (pdf.ts)

#### PdfOptions
PDF 생성 옵션.

```typescript
export interface PdfOptions {
  format?: 'A4' | 'Letter';
  orientation?: 'portrait' | 'landscape';
  includeMap?: boolean; // 지도 포함 여부
  includePhotos?: boolean; // 장소 사진 포함 여부
  language?: 'ko' | 'en'; // 언어 (한국어/영어)
}

export interface PdfMetadata {
  title: string;
  author: string;
  subject: string;
  creator: string; // "AI TravelTailor"
  createdAt: string; // ISO 8601 format
}
```

## 사용 가이드

### Frontend에서 사용
```typescript
// 1. 타입 import
import type { Trip, ApiResponse, PaginationParams } from '@traveltailor/shared/types';

// 2. API 호출 시 타입 적용
const response: ApiResponse<Trip> = await api.get('/v1/trips/123');

// 3. Zod 스키마와 함께 사용 (런타임 검증)
import { z } from 'zod';
import type { Trip } from '@traveltailor/shared/types';

const TripSchema = z.object({
  id: z.string(),
  destination: z.string(),
  startDate: z.string().datetime(),
  // ...
}) satisfies z.ZodType<Trip>;

const trip = TripSchema.parse(response.data);
```

### Backend에서 참조 (Python)
Backend는 Python이므로 TypeScript 타입을 직접 사용할 수 없지만, Pydantic 스키마 작성 시 참조 가이드로 사용합니다.

```python
# backend/src/schemas/trip.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# TypeScript Trip 타입을 참조하여 Pydantic 스키마 작성
class TripResponse(BaseModel):
    id: str
    user_id: str
    destination: str
    start_date: datetime  # TypeScript: string (ISO 8601)
    end_date: datetime
    budget: float  # TypeScript: number
    status: str  # TypeScript: TripStatus enum
    preferences: dict  # TypeScript: Preferences
    itinerary: dict  # TypeScript: Itinerary
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()  # ISO 8601 format으로 직렬화
        }
```

## 타입 추가/수정 절차

### 1. 새로운 타입 추가
```typescript
// shared/types/new-feature.ts
export interface NewFeature {
  id: string;
  name: string;
  // ...
}

// shared/types/index.ts
export * from './new-feature';
```

### 2. 기존 타입 수정
```typescript
// Before
export interface Trip {
  id: string;
  destination: string;
}

// After (새 필드 추가)
export interface Trip {
  id: string;
  destination: string;
  tags?: string[]; // 선택적 필드로 추가 (하위 호환성 유지)
}
```

### 3. 버전 관리
- **Breaking Change**: 필수 필드 추가, 필드 제거, 타입 변경 → Major 버전 업데이트 (v1.0.0 → v2.0.0)
- **Non-Breaking Change**: 선택적 필드 추가, Enum 값 추가 → Minor 버전 업데이트 (v1.0.0 → v1.1.0)
- **Bug Fix**: 타입 오류 수정, 문서 수정 → Patch 버전 업데이트 (v1.0.0 → v1.0.1)

### 4. 동기화
- **Frontend**: `package.json`에서 `@traveltailor/shared` 버전 업데이트 후 `pnpm install`
- **Backend**: `shared/types` 변경 후 Pydantic 스키마 수정 (수동)

## 중요 규칙 및 제약사항

### 타입 정의 원칙
1. **명확한 네이밍**: 타입 이름은 용도를 명확히 반영 (예: `TripResponse`, `CreateTripRequest`)
2. **선택적 필드**: 필수가 아닌 필드는 `?` 사용 (하위 호환성)
   ```typescript
   interface Place {
     id: string;        // 필수
     name: string;      // 필수
     website?: string;  // 선택
   }
   ```

3. **Enum vs Union Type**:
   - 백엔드와 동기화 필요 → `enum` 사용
   - 프론트엔드 전용 타입 → `union type` 사용
   ```typescript
   // Enum (백엔드와 동기화)
   export enum TripStatus {
     DRAFT = 'draft',
     CONFIRMED = 'confirmed',
   }

   // Union Type (프론트엔드 전용)
   type ViewMode = 'list' | 'grid' | 'map';
   ```

4. **날짜/시간**: ISO 8601 문자열 형식 사용 (`string`)
   ```typescript
   // ✅ 올바른 방법
   startDate: string; // "2025-10-23T12:00:00Z"

   // ❌ 잘못된 방법
   startDate: Date; // JSON 직렬화 불가
   ```

5. **금액**: 숫자 타입 + 통화 단위 명시 (주석)
   ```typescript
   budget: number; // 원화 (KRW)
   ```

### 백엔드 동기화
1. **Pydantic 스키마 우선**: TypeScript 타입은 Pydantic 스키마를 참조하여 작성
2. **필드명 변환**: Python `snake_case` ↔ TypeScript `camelCase` (자동 변환 미들웨어)
   ```python
   # Backend (Python)
   class TripResponse(BaseModel):
       user_id: str
       start_date: datetime

   # Frontend (TypeScript)
   interface Trip {
     userId: string;
     startDate: string;
   }
   ```

3. **타입 검증**: Zod 스키마로 런타임 검증 (프론트엔드)
   ```typescript
   import { z } from 'zod';
   import type { Trip } from '@traveltailor/shared/types';

   const TripSchema = z.object({
     id: z.string(),
     userId: z.string(),
     destination: z.string(),
     startDate: z.string().datetime(),
     // ...
   }) satisfies z.ZodType<Trip>;

   const trip = TripSchema.parse(apiResponse.data); // 런타임 검증
   ```

## 테스트
```typescript
// shared/types/__tests__/travel-plan.test.ts
import type { Trip, Itinerary } from '../travel-plan';

describe('Trip 타입', () => {
  it('올바른 Trip 객체를 생성할 수 있다', () => {
    const trip: Trip = {
      id: '123',
      userId: 'user-456',
      destination: '도쿄',
      startDate: '2025-10-23T00:00:00Z',
      endDate: '2025-10-26T00:00:00Z',
      budget: 1000000,
      status: TripStatus.CONFIRMED,
      preferences: { /* ... */ },
      itinerary: { /* ... */ },
      createdAt: '2025-10-23T12:00:00Z',
      updatedAt: '2025-10-23T12:00:00Z',
    };

    expect(trip.destination).toBe('도쿄');
  });
});
```

## 배포
```bash
cd shared/types
npm version patch  # 버전 업데이트
npm publish        # npm private registry에 배포 (선택)

# 또는 로컬 경로 참조
# frontend/package.json
{
  "dependencies": {
    "@traveltailor/shared": "file:../../shared/types"
  }
}
```

## 문제 해결

### 자주 발생하는 오류

1. **Type mismatch between frontend and backend**
   - 원인: Backend Pydantic 스키마와 TypeScript 타입 불일치
   - 해결: 백엔드 응답을 확인하고 TypeScript 타입 업데이트

2. **Circular dependency**
   - 원인: 타입 간 순환 참조
   - 해결: `type` 키워드로 지연 참조 사용
   ```typescript
   // 순환 참조 발생
   export interface Place {
     relatedPlaces: Place[];
   }

   // 해결
   export interface Place {
     relatedPlaces: Array<Place>;
   }
   ```

3. **Enum value mismatch**
   - 원인: Backend Enum 값과 TypeScript Enum 값 불일치
   - 해결: Backend `choices` 확인 후 TypeScript Enum 동기화

## 추가 리소스
- [TypeScript 핸드북](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Pydantic 문서](https://docs.pydantic.dev/)
- [Zod 문서](https://zod.dev/)
- [ISO 8601 날짜 형식](https://en.wikipedia.org/wiki/ISO_8601)
