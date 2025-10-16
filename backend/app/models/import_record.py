"""
导入记录模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class ImportRecord(Base):
    """批量导入记录表"""
    __tablename__ = "import_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String(255))
    total_rows = Column(Integer)
    success_rows = Column(Integer)
    failed_rows = Column(Integer)
    error_details = Column(JSON)  # 使用通用 JSON 类型，支持 SQLite 和 PostgreSQL
    imported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ImportRecord {self.file_name}>"

