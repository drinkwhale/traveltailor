# Repository Guidelines

## Project Structure & Module Organization
The repository is split into `backend/` (FastAPI services, Alembic migrations, Python tests), `frontend/` (Next.js app, UI components, Playwright specs), and `shared/` (cross-platform types). Reference docs live in `specs/` and `docs/`. Keep feature-specific assets close to the owning module (e.g., `backend/src/services/ai/`, `frontend/src/components/map/`). Prefer adding new shared types under `shared/types/` so both stacks stay synchronized.

## Build, Test, and Development Commands
Backend: `uv run uvicorn src.main:app --reload` launches the API, `uv run alembic upgrade head` applies migrations, and `uv run pytest` runs the test suite. Frontend: `pnpm dev` starts the Next.js dev server, `pnpm build` produces a production bundle, and `pnpm exec playwright test` executes E2E coverage. Run these from their respective directories after copying `.env` templates.

## Coding Style & Naming Conventions
Python code follows 4-space indentation with Ruff + Black enforcing formatting (`uv run ruff check`, `uv run black`). Use snake_case for modules/functions and PascalCase for Pydantic models. TypeScript/React uses 2-space indentation; ESLint + Prettier guard formatting (`pnpm lint`, `pnpm format` if introduced). Favor kebab-case filenames for React routes and PascalCase for shared components (e.g., `DailyItinerary.tsx`).

## Testing Guidelines
Write pytest modules under `backend/tests/` using the `test_<feature>.py` pattern. Async tests should leverage `pytest-asyncio`. Frontend unit tests belong in `frontend/tests/unit/`, while Playwright specs sit in `frontend/tests/e2e/`. Aim to cover critical flows (plan creation, map rendering, PDF download) and note gaps in PR descriptions. Run smoke tests before opening a PR.

## Commit & Pull Request Guidelines
Craft commit messages in present-tense imperative (e.g., `Add travel plan fallback template`). Each PR should describe the change, link relevant task IDs (T###) from `specs/001-ai-travel-planner/tasks.md`, and provide screenshots or terminal output for UI or API-affecting updates. Confirm lint and test status in the description. Avoid mixing backend and frontend changes unless the work demands synchronized updates.

## Security & Configuration Tips
Never commit `.env` files; rely on `.env.example` and `.env.local.example`. Rotate API keys regularly and document access in `docs/external-apis.md`. When adding new secrets, update both README quick-start instructions and the deployment checklist in `docs/`.
