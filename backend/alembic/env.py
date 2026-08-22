import asyncio
import os
import sys
from logging.config import fileConfig

# Ensure the project root (backend) is in PYTHONPATH for imports like 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        pass  # Logging config optional

# add your model's MetaData object here
# for 'autogenerate' support
# from app.models import Base  # adjust as needed
from app.core.database import Base

def get_url() -> str:
    """Return the database URL.
    Prefer environment variable DATABASE_URL, fall back to settings.
    """
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# target metadata for 'autogenerate'
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py.
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't need a DB driver at all.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations in online mode.
    Called by ``run_async_migrations`` with a DB connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Create an async engine and run migrations.
    ``async_engine_from_config`` reads the alembic.ini ``sqlalchemy.url``
    setting, which we override with ``get_url``.
    """
    from sqlalchemy.ext.asyncio import async_engine_from_config
    cfg = config.get_section(config.config_ini_section) or {}
    cfg["sqlalchemy.url"] = get_url()
    connectable: AsyncEngine = async_engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    Uses asyncio to run the async engine.
    """
    asyncio.run(run_async_migrations())

# Determine mode and run appropriate function
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
