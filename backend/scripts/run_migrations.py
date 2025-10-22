"""Utility script to run Alembic migrations using production settings."""
from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def run() -> None:
    project_root = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run()
