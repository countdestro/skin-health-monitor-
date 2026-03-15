from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from alembic import context
from app.config import get_settings
from app.database import Base
from app import models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata
settings = get_settings()
# Use sync URL for Alembic (postgresql:// with psycopg2)
sync_url = settings.postgres_url.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")
config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))
    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
