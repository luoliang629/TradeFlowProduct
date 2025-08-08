"""Alembic环境配置."""

import asyncio
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.models.base import BaseModel

# Alembic Config对象提供对.ini文件中值的访问
config = context.config

# 解释.ini文件的日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 为'autogenerate'支持添加您的模型的MetaData
target_metadata = BaseModel.metadata

# 其他在env.py中的值，根据需要由env.py定义，可以通过用户配置变化获得。
# 我的方法是为每个环境使用指定特定命名方案的.ini文件
# 在代码中明确给出URL，或者我可以使用 SQLALCHEMY_URL 环境变量


def get_url() -> str:
    """获取数据库URL."""
    return settings.database_url


def run_migrations_offline() -> None:
    """在'offline'模式下运行迁移。

    这配置了上下文只需要一个URL
    而不需要Engine，虽然Engine也是可接受的
    在这里。通过跳过Engine创建
    我们甚至不需要DBAPI可用。

    从字符串中调用context.execute()以发出DDL；以及
    context.begin_transaction()以获得更详细的控制。
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """运行实际的迁移."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在async模式下创建Engine并与连接关联以运行迁移."""
    connectable = create_async_engine(get_url())

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在'online'模式下运行迁移。

    在这种场景下我们需要创建一个Engine
    并将连接与上下文关联。
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()