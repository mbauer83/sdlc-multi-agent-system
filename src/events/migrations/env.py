"""
Alembic migration environment.

Supports both offline (--sql output) and online (live SQLite connection) modes.
The database URL is read from:
  1. SDLC_DB_URL environment variable (allows per-engagement override in CI)
  2. alembic.ini sqlalchemy.url setting

Usage:
  # Upgrade the ENG-001 engagement DB (dev default):
  uv run alembic upgrade head

  # Upgrade a specific engagement DB:
  SDLC_DB_URL="sqlite:///engagements/ENG-042/workflow.db" uv run alembic upgrade head

  # Generate a new migration:
  uv run alembic revision --autogenerate -m "add column"
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Alembic config object — access to alembic.ini values
config = context.config

# Honour logging config in alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override URL from environment variable if set
db_url: str = os.getenv("SDLC_DB_URL") or config.get_main_option("sqlalchemy.url", "sqlite:///:memory:")


def run_migrations_offline() -> None:
    """
    Run migrations without a live DB connection.

    Writes DDL SQL to stdout — useful for review or applying to managed databases.
    """
    context.configure(
        url=db_url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},  # SQLite thread-safety for tests
        poolclass=pool.NullPool,                     # No connection pooling for SQLite
    )
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
