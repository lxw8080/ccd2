"""
File Storage Service
"""
import os
import uuid
from pathlib import Path
from typing import BinaryIO, Optional
from datetime import datetime, timedelta

from ..config import settings


class StorageService:
    """
    File storage service supporting local, OSS, and MinIO
    """
    
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.upload_dir = Path(settings.UPLOAD_DIR)
        
        if self.storage_type == "local":
            self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_file_path(self, original_filename: str, customer_id: str, document_type_code: str = None) -> str:
        """
        Generate a unique file path
        Format: {customer_id}/{document_type_code}/{uuid}{ext}
        """
        # Get file extension
        ext = Path(original_filename).suffix.lower()

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{ext}"

        # Organize by customer and document type
        if document_type_code:
            file_path = f"{customer_id}/{document_type_code}/{unique_filename}"
        else:
            # Fallback to date-based organization
            date_path = datetime.now().strftime("%Y/%m/%d")
            file_path = f"{customer_id}/{date_path}/{unique_filename}"

        return file_path
    
    async def save_file(
        self,
        file: BinaryIO,
        file_path: str
    ) -> str:
        """
        Save file to storage
        Returns the file path
        """
        if self.storage_type == "local":
            return await self._save_local(file, file_path)
        elif self.storage_type == "oss":
            return await self._save_oss(file, file_path)
        elif self.storage_type == "minio":
            return await self._save_minio(file, file_path)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    async def _save_local(self, file: BinaryIO, file_path: str) -> str:
        """
        Save file to local storage
        """
        full_path = self.upload_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            # Read content if it's a file-like object
            if hasattr(file, 'read'):
                content = file.read()
                if hasattr(content, '__await__'):
                    content = await content
            else:
                content = file
            f.write(content)

        return file_path

    def get_local_file_path(self, file_path: str) -> Path:
        """
        Get the full local file path
        """
        return self.upload_dir / file_path
    
    async def _save_oss(self, file: BinaryIO, file_path: str) -> str:
        """
        Save file to Aliyun OSS
        """
        # TODO: Implement OSS upload
        # import oss2
        # auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
        # bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
        # bucket.put_object(file_path, file)
        raise NotImplementedError("OSS storage not implemented yet")
    
    async def _save_minio(self, file: BinaryIO, file_path: str) -> str:
        """
        Save file to MinIO
        """
        # TODO: Implement MinIO upload
        # from minio import Minio
        # client = Minio(
        #     settings.MINIO_ENDPOINT,
        #     access_key=settings.MINIO_ACCESS_KEY,
        #     secret_key=settings.MINIO_SECRET_KEY,
        #     secure=settings.MINIO_SECURE
        # )
        # client.put_object(settings.MINIO_BUCKET_NAME, file_path, file, -1)
        raise NotImplementedError("MinIO storage not implemented yet")
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage
        """
        if self.storage_type == "local":
            return await self._delete_local(file_path)
        elif self.storage_type == "oss":
            return await self._delete_oss(file_path)
        elif self.storage_type == "minio":
            return await self._delete_minio(file_path)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    async def _delete_local(self, file_path: str) -> bool:
        """
        Delete file from local storage
        """
        full_path = self.upload_dir / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    async def _delete_oss(self, file_path: str) -> bool:
        """
        Delete file from OSS
        """
        # TODO: Implement OSS delete
        raise NotImplementedError("OSS storage not implemented yet")
    
    async def _delete_minio(self, file_path: str) -> bool:
        """
        Delete file from MinIO
        """
        # TODO: Implement MinIO delete
        raise NotImplementedError("MinIO storage not implemented yet")
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Get file URL (signed URL for cloud storage)
        """
        if self.storage_type == "local":
            # For local storage, return a relative URL
            return f"/api/files/{file_path}"
        elif self.storage_type == "oss":
            return self._get_oss_url(file_path, expires_in)
        elif self.storage_type == "minio":
            return self._get_minio_url(file_path, expires_in)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def _get_oss_url(self, file_path: str, expires_in: int) -> str:
        """
        Get signed URL from OSS
        """
        # TODO: Implement OSS signed URL
        # import oss2
        # auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
        # bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
        # return bucket.sign_url('GET', file_path, expires_in)
        raise NotImplementedError("OSS storage not implemented yet")
    
    def _get_minio_url(self, file_path: str, expires_in: int) -> str:
        """
        Get signed URL from MinIO
        """
        # TODO: Implement MinIO signed URL
        # from minio import Minio
        # from datetime import timedelta
        # client = Minio(...)
        # return client.presigned_get_object(
        #     settings.MINIO_BUCKET_NAME,
        #     file_path,
        #     expires=timedelta(seconds=expires_in)
        # )
        raise NotImplementedError("MinIO storage not implemented yet")


# Singleton instance
storage_service = StorageService()

