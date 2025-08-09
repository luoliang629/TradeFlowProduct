"""文件管理相关模型定义."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, 
    Float, Integer, String, Text, ForeignKey
)
from sqlalchemy.sql import func

from app.models.base import Base


class FileStatus(str, Enum):
    """文件状态枚举."""
    
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


class FileType(str, Enum):
    """文件类型枚举."""
    
    # 文档类
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    RTF = "rtf"
    
    # 表格类
    XLS = "xls"
    XLSX = "xlsx"
    CSV = "csv"
    
    # 演示类
    PPT = "ppt"
    PPTX = "pptx"
    
    # 图像类
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    SVG = "svg"
    
    # 代码类
    PY = "py"
    JS = "js"
    TS = "ts"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RS = "rs"
    
    # 标记类
    MD = "md"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    HTML = "html"
    CSS = "css"
    
    # 压缩类
    ZIP = "zip"
    RAR = "rar"
    TAR = "tar"
    GZ = "gz"
    
    # 其他
    OTHER = "other"


class File(Base):
    """文件模型."""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息
    file_name = Column(String(255), nullable=False, comment="文件名")
    original_name = Column(String(255), nullable=False, comment="原始文件名")
    file_type = Column(
        SQLEnum(FileType),
        default=FileType.OTHER,
        nullable=False,
        comment="文件类型"
    )
    mime_type = Column(String(100), comment="MIME类型")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    
    # 存储信息
    storage_path = Column(String(500), nullable=False, comment="存储路径")
    storage_bucket = Column(String(100), nullable=False, comment="存储桶名称")
    storage_key = Column(String(500), nullable=False, unique=True, comment="存储键")
    
    # 用户关联
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    conversation_id = Column(String(100), index=True, comment="对话ID")
    
    # 元数据
    checksum = Column(String(64), comment="文件校验和")
    encoding = Column(String(20), comment="文件编码")
    
    # 预览信息
    preview_url = Column(String(500), comment="预览URL")
    thumbnail_url = Column(String(500), comment="缩略图URL")
    page_count = Column(Integer, comment="页数（文档类）")
    
    # 处理信息
    status = Column(
        SQLEnum(FileStatus),
        default=FileStatus.UPLOADING,
        nullable=False,
        comment="文件状态"
    )
    error_message = Column(Text, comment="错误信息")
    processed_at = Column(DateTime(timezone=True), comment="处理完成时间")
    
    # 标签和描述
    tags = Column(Text, comment="标签（逗号分隔）")
    description = Column(Text, comment="文件描述")
    
    # 访问控制
    is_public = Column(Boolean, default=False, comment="是否公开")
    expires_at = Column(DateTime(timezone=True), comment="过期时间")
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<File {self.file_name}>"
    
    @property
    def is_image(self) -> bool:
        """是否为图片文件."""
        return self.file_type in [
            FileType.JPG, FileType.JPEG, FileType.PNG,
            FileType.GIF, FileType.BMP, FileType.SVG
        ]
    
    @property
    def is_document(self) -> bool:
        """是否为文档文件."""
        return self.file_type in [
            FileType.PDF, FileType.DOC, FileType.DOCX,
            FileType.TXT, FileType.RTF
        ]
    
    @property
    def is_spreadsheet(self) -> bool:
        """是否为表格文件."""
        return self.file_type in [
            FileType.XLS, FileType.XLSX, FileType.CSV
        ]
    
    @property
    def is_code(self) -> bool:
        """是否为代码文件."""
        return self.file_type in [
            FileType.PY, FileType.JS, FileType.TS,
            FileType.JAVA, FileType.CPP, FileType.C,
            FileType.GO, FileType.RS
        ]
    
    @property
    def file_size_mb(self) -> float:
        """文件大小（MB）."""
        return self.file_size / (1024 * 1024) if self.file_size else 0