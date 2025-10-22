# AI Pipeline Load Test Plan

## 목표
- 전체 파이프라인 응답 시간 30초 SLA 검증
- TPS 5 기준에서 안정성 확인
- 캐싱(Preferences, Places) 효과 측정

## 환경
- FastAPI + Uvicorn 4 worker
- PostgreSQL + Redis (Docker Compose)
- Locust 2.30, k6 0.49

## 시나리오
1. 사용자 로그인 → CSRF 토큰 획득
2. `/v1/travel-plans` POST 호출 (세션 쿠키 포함)
3. 상태 Polling `/v1/travel-plans/{id}/status`
4. 결과 조회 `/v1/travel-plans/{id}`

## 메트릭
| 구분 | 목표 | 설명 |
| --- | --- | --- |
| p95 생성 시간 | ≤ 25초 | `generation_time_seconds` 필드 기반 |
| 에러율 | < 1% | 5xx + 4xx 비율 |
| AI 토큰 사용 | 20% 감소 | Redis 캐시 전후 비교 |
| CPU/메모리 | 알람 임계치 대비 70% 이하 | \- |

## 절차
1. `docker-compose up --build`
2. `locust -f tests/load/ai_travel_plan.py --headless -u 50 -r 5 -t 10m`
3. k6 스모크 테스트 `k6 run tests/load/ai_smoke.js`
4. Prometheus 스크레이프 → Grafana 대시보드 확인
5. 결과 요약 후 회귀 테스트 자동화 파이프라인에 첨부

## 회귀 기준
- SLA 위반 시 백엔드 프로파일링 및 캐시 키 히트율 점검
- Redis 미스율 40% 초과 시 키 전략 재검토
- API p99 > 400ms → SQL 쿼리 플랜 및 인덱스 재평가
