"""文件管理服务."""

import hashlib
import io
import mimetypes
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import BinaryIO, List, Optional, Tuple
from PIL import Image
import magic

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.logging import get_logger
from app.models.file import File, FileStatus, FileType
from app.utils.minio_client import minio_client
from app.config import settings

logger = get_logger(__name__)


class FileService:
    """文件服务类."""
    
    # 支持的文件扩展名映射
    EXTENSION_MAP = {
        ".pdf": FileType.PDF,
        ".doc": FileType.DOC,
        ".docx": FileType.DOCX,
        ".txt": FileType.TXT,
        ".rtf": FileType.RTF,
        ".xls": FileType.XLS,
        ".xlsx": FileType.XLSX,
        ".csv": FileType.CSV,
        ".ppt": FileType.PPT,
        ".pptx": FileType.PPTX,
        ".jpg": FileType.JPG,
        ".jpeg": FileType.JPEG,
        ".png": FileType.PNG,
        ".gif": FileType.GIF,
        ".bmp": FileType.BMP,
        ".svg": FileType.SVG,
        ".py": FileType.PY,
        ".js": FileType.JS,
        ".ts": FileType.TS,
        ".java": FileType.JAVA,
        ".cpp": FileType.CPP,
        ".c": FileType.C,
        ".go": FileType.GO,
        ".rs": FileType.RS,
        ".md": FileType.MD,
        ".json": FileType.JSON,
        ".xml": FileType.XML,
        ".yaml": FileType.YAML,
        ".yml": FileType.YAML,
        ".html": FileType.HTML,
        ".css": FileType.CSS,
        ".zip": FileType.ZIP,
        ".rar": FileType.RAR,
        ".tar": FileType.TAR,
        ".gz": FileType.GZ,
    }
    
    # 最大文件大小（MB）
    MAX_FILE_SIZE = {
        "image": 10,
        "document": 50,
        "spreadsheet": 20,
        "code": 5,
        "archive": 100,
        "default": 10
    }
    
    def __init__(self):
        """初始化文件服务."""
        self.bucket_name = settings.MINIO_BUCKET_NAME
    
    def _get_file_type(self, filename: str) -> FileType:
        """根据文件名获取文件类型."""
        ext = Path(filename).suffix.lower()
        return self.EXTENSION_MAP.get(ext, FileType.OTHER)
    
    def _validate_file_size(self, file_size: int, file_type: FileType) -> bool:
        """验证文件大小."""
        max_size_mb = self.MAX_FILE_SIZE.get("default", 10)
        
        if file_type in [FileType.JPG, FileType.JPEG, FileType.PNG, FileType.GIF]:
            max_size_mb = self.MAX_FILE_SIZE["image"]
        elif file_type in [FileType.PDF, FileType.DOC, FileType.DOCX]:
            max_size_mb = self.MAX_FILE_SIZE["document"]
        elif file_type in [FileType.XLS, FileType.XLSX, FileType.CSV]:
            max_size_mb = self.MAX_FILE_SIZE["spreadsheet"]
        elif file_type in [FileType.ZIP, FileType.RAR, FileType.TAR]:
            max_size_mb = self.MAX_FILE_SIZE["archive"]
        
        return file_size <= max_size_mb * 1024 * 1024
    
    def _calculate_checksum(self, file_data: bytes) -> str:
        """计算文件校验和."""
        return hashlib.sha256(file_data).hexdigest()
    
    def _detect_mime_type(self, file_data: bytes) -> str:
        """检测文件MIME类型."""
        try:
            mime = magic.Magic(mime=True)
            return mime.from_buffer(file_data)
        except:
            return "application/octet-stream"
    
    async def upload_file(
        self,
        db: AsyncSession,
        file: UploadFile,
        user_id: int,
        conversation_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[File]:
        """上传文件."""
        try:
            # 读取文件内容
            file_data = await file.read()
            file_size = len(file_data)
            
            # 获取文件类型
            file_type = self._get_file_type(file.filename)
            
            # 验证文件大小
            if not self._validate_file_size(file_size, file_type):
                logger.warning(f"File too large: {file.filename}")
                return None
            
            # 生成存储信息
            file_id = str(uuid.uuid4())
            storage_key = f"{user_id}/{file_id}/{file.filename}"
            
            # 计算校验和
            checksum = self._calculate_checksum(file_data)
            
            # 检测MIME类型
            mime_type = self._detect_mime_type(file_data)
            
            # 创建文件记录
            file_record = File(
                file_name=f"{file_id}_{file.filename}",
                original_name=file.filename,
                file_type=file_type,
                mime_type=mime_type,
                file_size=file_size,
                storage_path=f"minio://{self.bucket_name}/{storage_key}",
                storage_bucket=self.bucket_name,
                storage_key=storage_key,
                user_id=user_id,
                conversation_id=conversation_id,
                checksum=checksum,
                description=description,
                tags=",".join(tags) if tags else None,
                status=FileStatus.UPLOADING
            )
            
            db.add(file_record)
            await db.flush()
            
            # 上传到MinIO
            success = await minio_client.upload_file(
                self.bucket_name,
                storage_key,
                io.BytesIO(file_data),
                file_size,
                content_type=mime_type
            )
            
            if success:
                # 更新状态
                file_record.status = FileStatus.PROCESSING
                await db.commit()
                
                # 异步处理文件（生成预览等）
                await self._process_file(db, file_record, file_data)
                
                return file_record
            else:
                file_record.status = FileStatus.ERROR
                file_record.error_message = "Failed to upload to storage"
                await db.commit()
                return None
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            await db.rollback()
            return None
    
    async def _process_file(
        self,
        db: AsyncSession,
        file_record: File,
        file_data: bytes
    ) -> None:
        """处理文件（生成预览、缩略图等）."""
        try:
            # 根据文件类型进行处理
            if file_record.is_image:
                await self._process_image(db, file_record, file_data)
            elif file_record.file_type == FileType.PDF:
                await self._process_pdf(db, file_record, file_data)
            
            # 生成预览URL
            preview_url = await minio_client.get_presigned_url(
                self.bucket_name,
                file_record.storage_key,
                expires=3600  # 1小时
            )
            
            file_record.preview_url = preview_url
            file_record.status = FileStatus.READY
            file_record.processed_at = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to process file: {e}")
            file_record.status = FileStatus.ERROR
            file_record.error_message = str(e)
            await db.commit()
    
    async def _process_image(
        self,
        db: AsyncSession,
        file_record: File,
        file_data: bytes
    ) -> None:
        """处理图片文件."""
        try:
            # 打开图片
            image = Image.open(io.BytesIO(file_data))
            
            # 生成缩略图
            thumbnail = image.copy()
            thumbnail.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # 保存缩略图
            thumbnail_io = io.BytesIO()
            thumbnail_format = image.format or "JPEG"
            thumbnail.save(thumbnail_io, format=thumbnail_format)
            thumbnail_data = thumbnail_io.getvalue()
            
            # 上传缩略图
            thumbnail_key = f"{file_record.storage_key}_thumbnail"
            await minio_client.upload_file(
                self.bucket_name,
                thumbnail_key,
                io.BytesIO(thumbnail_data),
                len(thumbnail_data),
                content_type=f"image/{thumbnail_format.lower()}"
            )
            
            # 生成缩略图URL
            thumbnail_url = await minio_client.get_presigned_url(
                self.bucket_name,
                thumbnail_key,
                expires=3600
            )
            
            file_record.thumbnail_url = thumbnail_url
            
        except Exception as e:
            logger.error(f"Failed to process image: {e}")
    
    async def _process_pdf(
        self,
        db: AsyncSession,
        file_record: File,
        file_data: bytes
    ) -> None:
        """处理PDF文件."""
        # TODO: 实现PDF处理（页数统计、缩略图生成等）
        pass
    
    async def get_file(
        self,
        db: AsyncSession,
        file_id: int,
        user_id: Optional[int] = None
    ) -> Optional[File]:
        """获取文件信息."""
        try:
            query = select(File).where(File.id == file_id)
            
            if user_id:
                query = query.where(File.user_id == user_id)
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get file: {e}")
            return None
    
    async def list_files(
        self,
        db: AsyncSession,
        user_id: int,
        conversation_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[File]:
        """列出文件."""
        try:
            query = select(File).where(File.user_id == user_id)
            
            if conversation_id:
                query = query.where(File.conversation_id == conversation_id)
            
            query = query.order_by(File.created_at.desc())
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    async def download_file(
        self,
        db: AsyncSession,
        file_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Tuple[BinaryIO, str, str]]:
        """下载文件."""
        try:
            # 获取文件信息
            file_record = await self.get_file(db, file_id, user_id)
            if not file_record:
                return None
            
            # 从MinIO下载
            file_data = await minio_client.download_file(
                self.bucket_name,
                file_record.storage_key
            )
            
            if file_data:
                return (
                    io.BytesIO(file_data),
                    file_record.original_name,
                    file_record.mime_type or "application/octet-stream"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None
    
    async def delete_file(
        self,
        db: AsyncSession,
        file_id: int,
        user_id: Optional[int] = None
    ) -> bool:
        """删除文件."""
        try:
            # 获取文件信息
            file_record = await self.get_file(db, file_id, user_id)
            if not file_record:
                return False
            
            # 从MinIO删除
            await minio_client.delete_file(
                self.bucket_name,
                file_record.storage_key
            )
            
            # 删除缩略图（如果存在）
            if file_record.thumbnail_url:
                thumbnail_key = f"{file_record.storage_key}_thumbnail"
                await minio_client.delete_file(
                    self.bucket_name,
                    thumbnail_key
                )
            
            # 标记为删除状态（软删除）
            file_record.status = FileStatus.DELETED
            await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            await db.rollback()
            return False
    
    async def get_file_preview(
        self,
        db: AsyncSession,
        file_id: int,
        user_id: Optional[int] = None
    ) -> Optional[str]:
        """获取文件预览URL."""
        try:
            file_record = await self.get_file(db, file_id, user_id)
            if not file_record:
                return None
            
            # 如果预览URL过期，重新生成
            if not file_record.preview_url or self._is_url_expired(file_record.preview_url):
                preview_url = await minio_client.get_presigned_url(
                    self.bucket_name,
                    file_record.storage_key,
                    expires=3600
                )
                
                file_record.preview_url = preview_url
                await db.commit()
            
            return file_record.preview_url
            
        except Exception as e:
            logger.error(f"Failed to get file preview: {e}")
            return None
    
    def _is_url_expired(self, url: str) -> bool:
        """检查URL是否过期."""
        # TODO: 实现URL过期检查逻辑
        return False
    
    async def search_files(
        self,
        db: AsyncSession,
        user_id: int,
        query: str,
        file_types: Optional[List[FileType]] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[File]:
        """搜索文件."""
        try:
            stmt = select(File).where(File.user_id == user_id)
            
            # 文件名搜索
            if query:
                stmt = stmt.where(
                    File.original_name.ilike(f"%{query}%") |
                    File.description.ilike(f"%{query}%")
                )
            
            # 文件类型过滤
            if file_types:
                stmt = stmt.where(File.file_type.in_(file_types))
            
            # 标签过滤
            if tags:
                for tag in tags:
                    stmt = stmt.where(File.tags.ilike(f"%{tag}%"))
            
            stmt = stmt.order_by(File.created_at.desc())
            stmt = stmt.offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []


# 全局文件服务实例
file_service = FileService()