# Alembic Migration Guide

이 문서는 `backend` 서비스에서 Alembic 마이그레이션을 드라이런하고 롤백하는 절차를 정리합니다. 모든 명령은 `backend/` 디렉터리에서 `uv run`을 이용해 실행한다고 가정합니다.

## 사전 준비

- `.env` 또는 실행 환경에 `DATABASE_URL`이 설정되어 있어야 합니다.
- 로컬 테스트용으로는 Supabase 프로젝트 커넥션 문자열 또는 별도의 PostgreSQL 인스턴스를 사용할 수 있습니다.

## 드라이런 (SQL 출력 확인)

실제 테이블에 적용하기 전에 생성될 SQL을 확인하려면 `--sql` 플래그를 사용합니다. 출력은 터미널에 표시되므로 필요하면 리다이렉션하여 검토합니다.

```bash
uv run alembic upgrade head --sql > /tmp/migration_preview.sql
```

- 특정 리비전만 미리 보고 싶다면 `upgrade <revision> --sql` 형태로 실행합니다.
- SQL을 검토한 후 문제가 없다면 동일한 명령에서 `--sql`만 제거해 실제 업그레이드를 실행합니다.

## 업그레이드 적용

```bash
uv run alembic upgrade head
```

- 최신 리비전까지 순차 적용합니다.
- 여러 리비전을 차례로 올릴 때는 `head` 대신 `+1`, `+2` 등을 사용할 수 있습니다.

## 롤백 전략

마이그레이션 적용 후 문제가 발견되면 아래 순서로 롤백합니다.

1. 마지막으로 적용한 리비전을 확인합니다.

   ```bash
   uv run alembic current
   ```

2. 직전 상태로 되돌립니다.

   ```bash
   uv run alembic downgrade -1
   ```

3. 특정 리비전으로 돌아가려면 `downgrade <revision_id>` 형식을 사용합니다.

4. 롤백 후에는 애플리케이션이 기대대로 동작하는지 확인하고, 필요하면 SQL 덤프를 통해 상태를 복구합니다.

> **주의:** 롤백은 데이터 손실을 유발할 수 있습니다. 실서비스 환경에서는 백업을 확보한 후 진행하세요.

## 트러블슈팅

- `target database is not up to date` 에러가 발생하면 `uv run alembic history --verbose`로 리비전 체인을 확인하세요.
- 로컬 환경이 꼬였다고 판단되면 데이터베이스를 재생성하거나, `uv run alembic downgrade base`로 모든 리비전을 제거 후 재적용합니다.
