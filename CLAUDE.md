# traveltailor 개발 가이드라인

모든 기능 계획에서 자동 생성됨. 최종 업데이트: 2025-10-19

## 활성 기술 스택
- TypeScript 5.x (프론트엔드), Python 3.11+ (백엔드 AI 서비스) (001-ai-travel-planner)

## 프로젝트 구조
```
src/
tests/
```

## 주요 명령어
cd src [활성 기술에 대한 명령어만][활성 기술에 대한 명령어만] pytest [활성 기술에 대한 명령어만][활성 기술에 대한 명령어만] ruff check .

## 코드 스타일
TypeScript 5.x (프론트엔드), Python 3.11+ (백엔드 AI 서비스): 표준 규칙 준수

## 커밋 및 PR 지침
- **커밋 메시지 언어**: 한국어로 작성 (필요한 경우 괄호로 영어 병기 가능)
- **커밋 메시지 형식**: Conventional Commits 패턴 사용 (`fix:`, `feat:`, `refactor:`, `docs:` 등)
  - 예: `fix: PDF 생성 시 좌표 누락 처리 개선`, `feat: 새로운 기능 추가`
- **커밋 메시지 작성**: 간결하게 유지하고, 추가 맥락이 필요하면 본문에 한국어 설명 추가
- **PR 작성**:
  - 요약, 연관된 이슈 링크 포함
  - 검증 결과 (`uv run python -m pytest` 또는 `pnpm test` 출력) 포함
  - 필요시 UI 스크린샷 또는 API 샘플 첨부
- **머지 전**: CI 통과 확인, 리뷰 요청
- **머지 방식**: 히스토리 선형 유지를 위해 리베이스 선호 (머지 커밋보다)

## 최근 변경사항
- 001-ai-travel-planner: TypeScript 5.x (프론트엔드), Python 3.11+ (백엔드 AI 서비스) 추가됨

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
