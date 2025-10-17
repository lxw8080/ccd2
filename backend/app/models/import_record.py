"""
导入记录模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text
import uuid
from app.database import Base


class ImportRecord(Base):
    """批量导入记录表"""
    __tablename__ = "import_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255))
    total_rows = Column(Integer)
    success_rows = Column(Integer)
    failed_rows = Column(Integer)
    error_details = Column(JSON)  # 使用通用 JSON 类型，支持 SQLite 和 PostgreSQL
    imported_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<ImportRecord {self.file_name}>"

