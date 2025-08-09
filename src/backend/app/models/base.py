"""基础数据模型."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql import func


@as_declarative()
class Base:
    """基础模型类."""
    
    id: Any
    __name__: str
    
    # 生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        """根据类名生成表名."""
        return cls.__name__.lower()
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    def dict(self) -> dict:
        """转换为字典格式."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}