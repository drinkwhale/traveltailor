# TODO - AI TravelTailor

향후 개선 및 수정이 필요한 작업 목록입니다.

## 🔴 우선순위: 높음

### PostHog 분석 기능 재활성화
**관련 PR**: #12 (fix: PostHog Node.js 내장 모듈 빌드 오류 해결)
**문제**: PostHog-js 라이브러리가 Node.js 내장 모듈을 클라이언트 사이드에서 사용하려 해서 webpack 빌드 오류 발생
**현재 상태**: 임시로 완전 비활성화됨 ([frontend/src/components/providers/AppProviders.tsx:33-61](../../../frontend/src/components/providers/AppProviders.tsx))
**해결 방안 옵션**:
1. **PostHog-js 버전 업데이트**
   - 최신 버전에서 Node.js 모듈 의존성 제거되었는지 확인
   - 버전 업데이트 후 빌드 테스트

2. **서버 컴포넌트로 이동**
   - PostHog 초기화를 Server Component에서만 실행
   - 클라이언트 사이드에서는 이벤트만 전송

3. **대체 분석 도구 검토**
   - Vercel Analytics (Next.js 최적화)
   - Google Analytics 4
   - Plausible Analytics (프라이버시 중심)

**작업 항목**:
- [ ] PostHog-js 최신 버전 확인 및 릴리즈 노트 검토
- [ ] 테스트 환경에서 버전 업데이트 시도
- [ ] 실패 시 대체 도구 평가 및 선택
- [ ] 선택한 솔루션 구현 및 테스트
- [ ] 사용자 분석 기능 재활성화

**예상 작업 시간**: 2-4시간
**담당자**: TBD

---

## 🟡 우선순위: 중간

### 항공편 추천 기능 개선
**관련 PR**: [#9 - Skyscanner → Amadeus 마이그레이션](https://github.com/drinkwhale/traveltailor/pull/9#issue-3547446200)
**현재 상태**: Amadeus Test API 사용 중 (월 2,000 트랜잭션 무료)
**목적**: API 비용 절감, 사용자 경험 개선, 기능 확장

**작업 항목**:
- [ ] **Production API 전환**: Test → Production 엔드포인트 (월 2,000 트랜잭션 초과 시)
  - `backend/src/integrations/amadeus.py`의 BASE_URL 변경
  - Production API 키 발급 및 환경 변수 교체
  - 트랜잭션 모니터링 설정
- [ ] **캐싱 강화**: Redis TTL을 15분으로 확대하여 API 호출 최소화
  - 현재 5분 → 15분으로 변경
  - 캐시 적중률 모니터링 추가
  - 가격 변동 감지 및 캐시 무효화 전략 수립
- [ ] **Booking URL 개선**: Amadeus Booking Link API 연동 고려
  - 현재: Google Flights URL 사용 중
  - 대안: Amadeus Flight Create Orders API 또는 Affiliate 프로그램
- [ ] **다양한 항공편 옵션**: 편도, 다구간 검색 지원
  - `search_one_way()` 메서드 추가
  - `search_multi_city()` 메서드 추가 (여러 구간 지원)
  - 프론트엔드 UI 업데이트 (여행 유형 선택)
- [ ] **필터링 기능**: 항공사, 시간대, 환승 횟수별 필터
  - 항공사 필터 (`includedAirlineCodes` 파라미터)
  - 시간대 필터 (새벽/오전/오후/야간)
  - 환승 횟수 필터 (`nonStop`, `maxStops` 파라미터)
  - 좌석 등급 필터 (economy/business/first)
  - 가격 범위 필터 (클라이언트 사이드)

**예상 작업 시간**: 8-12시간
**담당자**: TBD

---

### Swagger UI OpenAPI JSON 생성 오류
**관련 이슈**: 백엔드 API 문서 페이지에서 500 에러 발생
**현재 상태**: Health Check API는 정상 작동하지만 `/openapi.json` 생성 실패
**오류 메시지**: `Failed to load API definition. Fetch error: Internal Server Error /openapi.json`
**영향 범위**: API 문서화 페이지 (http://localhost:8000/docs) 접근 불가

**작업 항목**:
- [ ] 백엔드 로그에서 OpenAPI 생성 관련 상세 에러 확인
- [ ] FastAPI 라우터/스키마 정의 검증
- [ ] Pydantic 모델 순환 참조 확인
- [ ] OpenAPI 스키마 수동 생성 테스트
- [ ] 문제 원인 파악 및 수정

**예상 작업 시간**: 1-2시간
**담당자**: TBD

---

## 🟢 우선순위: 낮음

### 개발 환경 스크립트 개선
**관련 파일**: [start-dev.sh](../../../start-dev.sh)
**현재 상태**: 기본 기능은 정상 작동

**개선 사항**:
- [ ] 로그 파일 회전 (rotation) 구현 (파일 크기 제한)
- [ ] 개별 서비스 재시작 옵션 추가 (`--restart-backend`, `--restart-frontend`)
- [ ] 환경 변수 검증 강화 (필수 키 누락 시 명확한 에러 메시지)
- [ ] 헬스 체크 자동화 (서버 시작 후 자동으로 /health 확인)
- [ ] Windows 지원 (start-dev.ps1 또는 start-dev.bat)

**예상 작업 시간**: 2-3시간
**담당자**: TBD

---

## 📝 문서화

### README 업데이트
- [ ] PostHog 비활성화 상태 명시
- [ ] 알려진 이슈 섹션 추가 (Swagger UI 오류)
- [ ] 트러블슈팅 가이드 확장

**예상 작업 시간**: 30분
**담당자**: TBD

---

## 완료된 작업

### ✅ 프론트엔드 빌드 오류 해결
**완료일**: 2025-10-24
**PR**: #12
**내용**: PostHog Node.js 모듈 충돌로 인한 webpack 빌드 오류 해결 (임시 비활성화)

---

## 작업 우선순위 가이드

- 🔴 **높음**: 사용자 기능에 직접 영향을 주거나 프로덕션 배포를 차단하는 이슈
- 🟡 **중간**: 개발 경험에 영향을 주지만 우회 가능한 이슈
- 🟢 **낮음**: 개선 사항 또는 Nice-to-have 기능

---

**마지막 업데이트**: 2025-10-24
**다음 검토 예정**: TBD
