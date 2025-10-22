import os
import sys
from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

pytestmark = pytest.mark.anyio("asyncio")


@pytest.fixture
def anyio_backend():
    return "asyncio"

# Ensure required env vars for settings before app import
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "supabase-key")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "supabase-service")
os.environ.setdefault("JWT_SECRET_KEY", "jwt-secret")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("GOOGLE_MAPS_API_KEY", "gmaps-test")
os.environ.setdefault("MAPBOX_ACCESS_TOKEN", "mapbox-test")

sys.modules.setdefault(
    "src.integrations.booking",
    SimpleNamespace(booking_affiliate=SimpleNamespace()),
)

if 'langchain.schema' not in sys.modules:
    sys.modules['langchain.schema'] = SimpleNamespace(
        HumanMessage=SimpleNamespace,
        SystemMessage=SimpleNamespace,
        AIMessage=SimpleNamespace,
    )


from src.main import app  # noqa: E402
from src.config.database import get_db  # noqa: E402
from src.core.csrf import require_csrf_token  # noqa: E402
from src.models.user import User  # noqa: E402
from src.api.v1 import auth as auth_module  # noqa: E402


class FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class FakeSession:
    def __init__(self):
        self._users: dict[str, User] = {}

    async def execute(self, stmt):
        where = stmt.whereclause
        if where is None:
            return FakeResult(None)
        column_name = where.left.name
        value = where.right.value
        if column_name == "email":
            user = next((u for u in self._users.values() if u.email == value), None)
            return FakeResult(user)
        if column_name == "id":
            user = self._users.get(str(value)) or self._users.get(str(value).lower())
            return FakeResult(user)
        return FakeResult(None)

    def add(self, instance: User) -> None:
        self._users[str(instance.id)] = instance

    async def commit(self):
        return None

    async def refresh(self, instance: User):
        return None

    async def close(self):
        return None


@pytest.fixture
async def fake_db():
    session = FakeSession()

    async def _get_db():
        yield session

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[require_csrf_token] = lambda: None
    original_hash = auth_module.get_password_hash
    original_verify = auth_module.verify_password
    auth_module.get_password_hash = lambda password: password
    auth_module.verify_password = lambda plain, hashed: plain == hashed
    yield session
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(require_csrf_token, None)
    auth_module.get_password_hash = original_hash
    auth_module.verify_password = original_verify


async def test_signup_login_cookie_flow(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"email": "user@example.com", "password": "securePass1!"}
        signup = await client.post("/v1/auth/signup", json=payload)
        assert signup.status_code == 201
        assert "tt_session" in signup.cookies

        login = await client.post("/v1/auth/login", json=payload)
        assert login.status_code == 200
        assert "tt_session" in login.cookies

        cookies = login.cookies
        profile = await client.get("/v1/auth/me", cookies=cookies)
        assert profile.status_code == 200
        assert profile.json()["data"]["email"] == "user@example.com"
