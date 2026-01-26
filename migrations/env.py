from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import text
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from alembic import context

from models import Base
import asyncio
import asyncpg
import json
import os

# with open("config/config.json", "r", encoding = "utf-8") as f:
#     config_data = json.load(f)

# username = config_data["database"]["username"]
# password = config_data["database"]["password"]
# database_name = config_data["database"]["database_name"]

load_dotenv()

database_url = os.getenv("DATABASE_URL_ENV")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", database_url)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


async def create_database_if_not_exists(database_url: str, database_name: str):
    # default_url = database_url.rsplit("/", 1)[0] + "/postgres"
    # engine = create_async_engine(default_url, poolclass=None)

    # async with engine.connect() as conn:
    #     result = await conn.execute(
    #         text("SELECT 1 FROM pg_database WHERE datname = :name"),
    #         {"name": database_name},
    #     )
    #     exists = result.scalar() is not None

    #     if not exists:
    #         conn_autocommit = await conn.execution_options(isolation_level="AUTOCOMMIT")

    #         await conn_autocommit.execute(text(f'CREATE DATABASE "{database_name}"'))
    #         print(f"Database '{database_name}' created.")

    # await engine.dispose()
    conn = await asyncpg.connect(
        user=username,
        password=password,
        host="localhost",
        port="5432",
        database=database_name,
    )

    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", database_name
    )

    if not exists:
        await conn.execute(f'CREATE DATABASE "{database_name}"')
        print(f"Database '{database_name}' created.")

    await conn.close()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # await create_database_if_not_exists(database_url, database_name)

    connectable: AsyncEngine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
