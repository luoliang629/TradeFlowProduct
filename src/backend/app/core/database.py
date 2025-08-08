"""数据库连接配置模块."""

from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# SQLAlchemy配置
Base = declarative_base()

# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1小时后回收连接
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# MongoDB配置
class MongoDB:
    """MongoDB连接管理器."""
    
    def __init__(self) -> None:
        """初始化MongoDB连接."""
        self._client: AsyncIOMotorClient = None
        self._database: AsyncIOMotorDatabase = None
    
    @property
    def client(self) -> AsyncIOMotorClient:
        """获取MongoDB客户端."""
        if not self._client:
            self._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
            )
        return self._client
    
    @property
    def database(self) -> AsyncIOMotorDatabase:
        """获取MongoDB数据库."""
        if not self._database:
            self._database = self.client[settings.mongodb_database_name]
        return self._database
    
    async def close(self) -> None:
        """关闭MongoDB连接."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")


# 全局MongoDB实例
mongodb = MongoDB()


async def get_mongodb() -> AsyncIOMotorDatabase:
    """获取MongoDB数据库实例."""
    return mongodb.database


# 数据库初始化和关闭事件
async def init_databases() -> None:
    """初始化数据库连接."""
    try:
        # 测试PostgreSQL连接
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        logger.info("PostgreSQL connection established")
        
        # 测试MongoDB连接
        await mongodb.client.admin.command('ping')
        logger.info(
            "MongoDB connection established",
            database=settings.mongodb_database_name
        )
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise


async def close_databases() -> None:
    """关闭数据库连接."""
    try:
        # 关闭PostgreSQL连接
        await engine.dispose()
        logger.info("PostgreSQL connection closed")
        
        # 关闭MongoDB连接
        await mongodb.close()
        
    except Exception as e:
        logger.error("Error closing database connections", error=str(e))
        raise