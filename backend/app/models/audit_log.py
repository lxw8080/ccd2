"""
审计日志模型
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
import uuid
from app.database import Base


class AuditLog(Base):
    """操作日志表"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    action = Column(String(50), nullable=False)  # upload, delete, approve, reject, create, update
    details = Column(JSON)  # 使用通用 JSON 类型，支持 SQLite 和 PostgreSQL
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"

