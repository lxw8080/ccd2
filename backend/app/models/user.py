"""
用户模型
"""
from sqlalchemy import Column, String, Boolean, DateTime
import uuid
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(100))
    role = Column(String(20), nullable=False, index=True)  # customer_service, reviewer, admin
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<User {self.username}>"

