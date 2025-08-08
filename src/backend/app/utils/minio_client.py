"""MinIO客户端配置模块."""

import io
from datetime import datetime, timedelta
from typing import BinaryIO, Dict, List, Optional, Tuple, Union

from minio import Minio
from minio.error import S3Error
from urllib3 import HTTPResponse

from app.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class MinIOClient:
    """MinIO客户端管理器."""
    
    def __init__(self) -> None:
        """初始化MinIO客户端."""
        self._client: Optional[Minio] = None
    
    @property
    def client(self) -> Minio:
        """获取MinIO客户端."""
        if not self._client:
            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return self._client
    
    async def ensure_bucket_exists(self, bucket_name: Optional[str] = None) -> bool:
        """确保存储桶存在，不存在则创建."""
        bucket = bucket_name or settings.MINIO_BUCKET_NAME
        
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                
                # 设置默认存储桶策略（公开读取）
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                            "Resource": f"arn:aws:s3:::{bucket}",
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket}/*",
                        },
                    ],
                }
                
                import json
                self.client.set_bucket_policy(bucket, json.dumps(policy))
                
                logger.info("MinIO bucket created", bucket=bucket)
            
            return True
            
        except S3Error as e:
            logger.error("MinIO bucket creation failed", bucket=bucket, error=str(e))
            raise ExternalServiceError(
                f"Failed to create bucket {bucket}",
                service="MinIO",
                details={"bucket": bucket, "error": str(e)}
            )
    
    async def upload_file(
        self,
        file_data: Union[bytes, BinaryIO],
        object_name: str,
        bucket_name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """上传文件到MinIO."""
        bucket = bucket_name or settings.MINIO_BUCKET_NAME
        
        try:
            await self.ensure_bucket_exists(bucket)
            
            # 处理文件数据
            if isinstance(file_data, bytes):
                file_stream = io.BytesIO(file_data)
                file_size = len(file_data)
            else:
                file_stream = file_data
                file_stream.seek(0, 2)  # 移到文件末尾
                file_size = file_stream.tell()
                file_stream.seek(0)  # 重置到文件开头
            
            # 设置默认metadata
            if not metadata:
                metadata = {}
            
            metadata.update({
                "uploaded_at": datetime.utcnow().isoformat(),
                "uploaded_by": "tradeflow-backend",
            })
            
            # 上传文件
            result = self.client.put_object(
                bucket,
                object_name,
                file_stream,
                file_size,
                content_type=content_type or "application/octet-stream",
                metadata=metadata,
            )
            
            # 生成文件访问URL
            file_url = f"http://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"
            
            logger.info(
                "File uploaded to MinIO",
                bucket=bucket,
                object_name=object_name,
                file_size=file_size,
                etag=result.etag
            )
            
            return file_url
            
        except S3Error as e:
            logger.error(
                "MinIO file upload failed",
                bucket=bucket,
                object_name=object_name,
                error=str(e)
            )
            raise ExternalServiceError(
                f"Failed to upload file {object_name}",
                service="MinIO",
                details={"bucket": bucket, "object": object_name, "error": str(e)}
            )
    
    async def download_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
    ) -> Tuple[bytes, Dict[str, str]]:
        """从MinIO下载文件."""
        bucket = bucket_name or settings.MINIO_BUCKET_NAME
        
        try:
            # 获取文件
            response: HTTPResponse = self.client.get_object(bucket, object_name)
            file_data = response.read()
            
            # 获取文件信息
            stat = self.client.stat_object(bucket, object_name)
            metadata = stat.metadata or {}
            
            logger.info(
                "File downloaded from MinIO",
                bucket=bucket,
                object_name=object_name,
                file_size=len(file_data)
            )
            
            return file_data, metadata
            
        except S3Error as e:
            logger.error(
                "MinIO file download failed",
                bucket=bucket,
                object_name=object_name,
                error=str(e)
            )
            raise ExternalServiceError(
                f"Failed to download file {object_name}",
                service="MinIO",
                details={"bucket": bucket, "object": object_name, "error": str(e)}
            )
        finally:
            response.close()
            response.release_conn()
    
    async def delete_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
    ) -> bool:
        """从MinIO删除文件."""
        bucket = bucket_name or settings.MINIO_BUCKET_NAME
        
        try:
            self.client.remove_object(bucket, object_name)
            
            logger.info(
                "File deleted from MinIO",
                bucket=bucket,
                object_name=object_name
            )
            
            return True
            
        except S3Error as e:
            logger.error(
                "MinIO file deletion failed",
                bucket=bucket,
                object_name=object_name,
                error=str(e)
            )
            raise ExternalServiceError(
                f"Failed to delete file {object_name}",
                service="MinIO",
                details={"bucket": bucket, "object": object_name, "error": str(e)}
            )
    
    async def get_file_info(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
    ) -> Dict[str, any]:
        """获取文件信息."""
        bucket = bucket_name or settings.MINIO_BUCKET_NAME
        
        try:
            stat = self.client.stat_object(bucket, object_name)
            
            return {
                "size": stat.size,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata or {},
                "version_id": stat.version_id,
            }
            
        except S3Error as e:
            logger.error(
                "MinIO file stat failed",
                bucket=bucket,
                object_name=object_name,
                error=str(e)
            )
            raise ExternalServiceError(
                f"Failed to get file info {object_name}",
                service="MinIO",
                details={"bucket": bucket, "object": object_name, "error": str(e)}
            )
    
    async def list_files(
        self,
        prefix: str = "",
        bucket_name: Optional[str] = None,
        recursive: bool = True,
    ) -> List[Dict[str, any]]:
        """列出文件."""
        bucket = bucket_name or settings.MINIO_BUCKET_NAME
        
        try:
            objects = self.client.list_objects(
                bucket, prefix=prefix, recursive=recursive
            )
            
            files = []
            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "etag": obj.etag,
                    "last_modified": obj.last_modified,
                    "content_type": obj.content_type,
                })
            
            logger.info(
                "Files listed from MinIO",
                bucket=bucket,
                prefix=prefix,
                count=len(files)
            )
            
            return files
            
        except S3Error as e:
            logger.error(
                "MinIO file listing failed",
                bucket=bucket,
                prefix=prefix,
                error=str(e)
            )
            raise ExternalServiceError(
                f"Failed to list files with prefix {prefix}",
                service="MinIO",
                details={"bucket": bucket, "prefix": prefix, "error": str(e)}
            )
    
    async def generate_presigned_url(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
        expires: timedelta = timedelta(hours=1),
        method: str = "GET",
    ) -> str:
        """生成预签名URL."""
        bucket = bucket_name or settings.MINIO_BUCKET_NAME
        
        try:
            if method.upper() == "GET":
                url = self.client.presigned_get_object(bucket, object_name, expires)
            elif method.upper() == "PUT":
                url = self.client.presigned_put_object(bucket, object_name, expires)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            logger.info(
                "Presigned URL generated",
                bucket=bucket,
                object_name=object_name,
                method=method,
                expires=expires.total_seconds()
            )
            
            return url
            
        except S3Error as e:
            logger.error(
                "MinIO presigned URL generation failed",
                bucket=bucket,
                object_name=object_name,
                error=str(e)
            )
            raise ExternalServiceError(
                f"Failed to generate presigned URL for {object_name}",
                service="MinIO",
                details={"bucket": bucket, "object": object_name, "error": str(e)}
            )


# 全局MinIO客户端实例
minio_client = MinIOClient()


def get_minio_client() -> MinIOClient:
    """获取MinIO客户端依赖."""
    return minio_client


# MinIO初始化事件
async def init_minio() -> None:
    """初始化MinIO连接和存储桶."""
    try:
        await minio_client.ensure_bucket_exists()
        logger.info("MinIO initialized successfully")
    except Exception as e:
        logger.error("MinIO initialization failed", error=str(e))
        raise