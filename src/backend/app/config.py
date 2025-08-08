"""应用配置管理模块."""

import secrets
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Environment(str, Enum):
    """环境枚举."""
    
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """应用配置类."""
    
    # 基础配置
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    LOG_LEVEL: str = "INFO"
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "TradeFlow Backend API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "B2B Trade Intelligence Assistant Backend API"
    
    # CORS配置
    CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: List[str] = ["*"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """处理CORS origins配置."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 数据库配置
    POSTGRES_URL: Optional[str] = None
    POSTGRES_TEST_URL: Optional[str] = None
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "tradeflow"
    MONGODB_TEST_DATABASE: str = "tradeflow_test"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TEST_URL: str = "redis://localhost:6379/1"
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "tradeflow-storage"
    
    # JWT配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # 外部服务配置
    GOOGLE_ADK_API_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    
    # 监控配置
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8001
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境."""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """是否为测试环境."""
        return self.ENVIRONMENT == Environment.TESTING
    
    @property
    def database_url(self) -> str:
        """获取数据库URL."""
        if self.is_testing and self.POSTGRES_TEST_URL:
            return self.POSTGRES_TEST_URL
        return self.POSTGRES_URL or ""
    
    @property
    def mongodb_database_name(self) -> str:
        """获取MongoDB数据库名称."""
        if self.is_testing:
            return self.MONGODB_TEST_DATABASE
        return self.MONGODB_DATABASE
    
    @property
    def redis_url(self) -> str:
        """获取Redis URL."""
        if self.is_testing:
            return self.REDIS_TEST_URL
        return self.REDIS_URL
    
    class Config:
        """Pydantic配置."""
        
        env_file = ".env"
        case_sensitive = True
        validate_assignment = True


# 全局配置实例
settings = Settings()