# External API Access & Cost Tracking

AI TravelTailor가 의존하는 외부 API의 계약 상태, 키 관리, 및 호출 비용 정보를 정리합니다. 모든 금액은 USD 기준이며 최신 공식 문서를 2024-10 시점에 확인해 작성했습니다.

| API | Env Vars | Access Status | Notes |
| --- | --- | --- | --- |
| Google Places | `GOOGLE_MAPS_API_KEY` | Active (Production key in Supabase Vault) | 도메인/서버 IP 제한 적용, 지도/Places 공용 프로젝트와 분리됨 |
| OpenAI | `OPENAI_API_KEY` | Active (Org: traveltailor-ai) | Usage cap 월 $300, rate-limit 5 RPS (gpt-4o-mini) |
| Mapbox | `MAPBOX_ACCESS_TOKEN` | Active (Team tier) | 스타일 토큰은 Frontend `.env.local`에서 별도 scope 사용 |
| Amadeus Flights | `AMADEUS_API_KEY`, `AMADEUS_API_SECRET` | Test (무료 티어) | Flight Offers Search API 사용, 월 2,000 트랜잭션 무료 |
| Booking.com Affiliate | `BOOKING_COM_AFFILIATE_ID` | Pending (제휴 승인 대기) | 승인 완료 시 예약 링크 트래킹, 현재 테스트용 `demo` ID |
| Agoda | `AGODA_API_KEY` | Sandbox (파트너 토큰) | Mock 응답 기반 개발, 월 500 호출 제한 |
| Supabase | `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY` | Active | Service role 키는 백엔드만 사용, row-level security 활성화 |

## Key Storage & Rotation

- 모든 비공개 키는 1Password `AI TravelTailor / Production` 볼트에 저장합니다.
- 로컬 개발 시 `.env.example`, `.env.local.example`를 복사 후 개인 키를 입력합니다. 실제 키 커밋 금지.
- 반기(6개월)마다 키 재발급을 진행하고, 변경 사항을 이 문서와 `docs/deployment-checklist.md`에 반영합니다.
- Amadeus/Agoda 키와 Booking 제휴 ID는 `TravelTailor / Partnerships` 금고에 복제 보관하며, 테스트 키와 운영 키를 명확히 구분합니다.

## 계약 상태 체크리스트

- Google Cloud 프로젝트 `traveltailor-core`에 Places API, Geocoding API, Maps Static API 활성화 완료. 결제 프로필: `TT Studio LLC`.
- OpenAI 계정에 사용량 알림(75%, 90%) 설정 완료. 조직 내 3명의 엔지니어만 API 키 생성 권한 보유.
- Mapbox 계정 월간 활동 이메일 리포트 구독. 예산 초과 시 자동 알림 Slack #alerts 채널로 전달.
- Supabase 프로젝트 `traveltailor-prod`의 서비스 롤 키는 FastAPI 서버에서만 사용하며, 인증된 사용자만 RLS 규칙에 따라 데이터 접근.

## 비용 및 쿼터 계산

| API | Unit Cost | Quota Assumption | Monthly Est. | Notes |
| --- | --- | --- | --- | --- |
| Google Places Text Search | $17.00 / 1000 requests | 3,000 req/일 | ~$1,530 | 10회/여행 플랜 × 300 플랜/일 기준 |
| Google Place Details | $17.00 / 1000 requests | 2,000 req/일 | ~$1,020 | Top 5 장소 상세 조회 가정 |
| Google Place Photos | $7.00 / 1000 calls | 5,000 call/일 | ~$1,050 | 썸네일 이미지만 로드 |
| OpenAI gpt-4o-mini | $0.15 / 1M input tokens<br>$0.60 / 1M output tokens | 200K in / 80K out tokens/일 | ~$162 | 1 플랜당 15K/6K 토큰 가정 |
| Mapbox Tiles | $0.50 / 1k map loads | 1,500 load/일 | ~$225 | 사용자 일정 조회 대비 5뷰/플랜 |
| Amadeus Flight Offers | Free (Test tier) | 500 call/일 | $0 | 월 2,000 트랜잭션 무료, Production 전환 시 유료 ($0.025/call) |
| Agoda Affiliate API | Revenue share (5%) | 300 call/일 | N/A | 제휴 확정 후 실매출 기반 수수료 정산 |
| Supabase Auth + DB | 포함 (Pro 플랜 $25/월) | 8GB 저장, 5M 요청 | $25 | 초과 시 자동 업그레이드 옵션 |

> 비용 계산은 예상 시나리오에 기반한 상한치입니다. 실제 사용량을 `backend/src/middleware/cost_tracking.py`와 Supabase 대시보드로 모니터링합니다.

## 운영 수칙

1. 새로운 스테이지(스테이징/프로덕션) 추가 시, 별도의 API 키를 생성하고 환경 변수 파일을 업데이트합니다.
2. 외부 API 스키마가 변경되면 `specs/` 내 계약 문서를 업데이트하고, 깨지는 테스트가 없는지 확인합니다.
3. 비용이 예산(월 $3,000)을 초과할 것으로 예상되면 PM에게 슬랙 경보를 전송하고, Fallback 전략(캐싱, 저비용 모델)을 가동합니다.
