"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用信息
    APP_NAME: str = "客户资料收集系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置（默认使用外部数据库；通过 .env 覆盖 DATABASE_URL）
    DATABASE_URL: str = "postgresql://ccd_user:ccd_password@localhost:5432/ccd_db"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # 文件存储配置
    STORAGE_TYPE: str = "local"  # local, oss, minio
    UPLOAD_DIR: str = "./uploads"
    
    # 阿里云OSS配置
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET_NAME: str = ""
    OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "ccd-files"
    MINIO_SECURE: bool = False
    
    # 文件上传限制
    MAX_FILE_SIZE: int = 20971520  # 20MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/server.log"

    # API配置
    API_KEY: str = ""

    # Flask环境
    FLASK_ENV: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 允许额外的环境变量


# 创建全局配置实例
settings = Settings()

