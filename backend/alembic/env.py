# Alembic配置文件
# 用于数据库迁移管理

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 导入配置和Base
from app.core.config import settings
from app.db.base import Base

# Alembic Config对象，提供访问.ini文件中的值
config = context.config

# 覆盖alembic.ini中的sqlalchemy.url为实际配置
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 解释Python日志配置文件
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的MetaData对象，用于自动生成迁移
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """以'离线'模式运行迁移（生成SQL脚本，不连接数据库）"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """以'在线'模式运行异步迁移（直接连接数据库）"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式入口（Async模式）"""
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
