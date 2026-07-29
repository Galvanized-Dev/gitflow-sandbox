"""Alembic env for the sandbox.

Builds the URL from the same FIDES__DATABASE__* variables the Talos release scripts
export (see verify-migration-reconcile.sh's alembic_env), so those scripts drive this
repo unmodified. No app models here — the sandbox only needs a real, migratable
database to prove migration *ordering*, which is what static down_revision checks
cannot see.
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _url() -> str:
    host = os.environ.get("FIDES__DATABASE__SERVER", "localhost")
    port = os.environ.get("FIDES__DATABASE__PORT", "5432")
    user = os.environ.get("FIDES__DATABASE__USER", "postgres")
    password = os.environ.get("FIDES__DATABASE__PASSWORD", "fides")
    db = os.environ.get("FIDES__DATABASE__DB", "fides")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    context.configure(url=_url(), literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    config.set_main_option("sqlalchemy.url", _url())
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
