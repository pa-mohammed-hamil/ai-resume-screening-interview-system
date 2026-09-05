from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.core.config import settings
from app.database.base import Base

# Import all models so that their tables are registered
# in Base.metadata before Alembic compares metadata.
from app.models import audit_log
from app.models import candidate
from app.models import interview
from app.models import job
from app.models import resume
from app.models import score
from app.models import user


# Alembic Config object
config = context.config


# Configure logging if an Alembic config file exists.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata used by Alembic autogenerate.
target_metadata = Base.metadata


def get_database_url() -> str:
    """
    Get the database URL from application settings.

    Alembic uses a synchronous driver for migrations.
    """

    url = settings.DATABASE_URL

    # Convert async PostgreSQL URL to sync PostgreSQL URL.
    if url.startswith(
        "postgresql+asyncpg://"
    ):
        url = url.replace(
            "postgresql+asyncpg://",
            "postgresql+psycopg://",
            1,
        )

    return url


def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    """

    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations using an active database connection.
    """

    configuration = config.get_section(
        config.config_ini_section
    )

    if configuration is None:
        configuration = {}

    configuration[
        "sqlalchemy.url"
    ] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()