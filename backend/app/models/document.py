"""
文档模型
"""
from sqlalchemy import Column, String, Boolean, Integer, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class DocumentType(Base):
    """资料类型表"""
    __tablename__ = "document_types"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # identity, financial, credit, other
    description = Column(Text)
    is_required = Column(Boolean, default=False)  # 是否必须上传
    allowed_file_types = Column(String(200))  # 允许的文件类型，逗号分隔，如：jpg,png,pdf
    max_file_size = Column(Integer, default=10485760)  # 最大文件大小（字节），默认10MB
    min_files = Column(Integer, default=1)  # 最少文件数量
    max_files = Column(Integer, default=1)  # 最多文件数量
    is_active = Column(Boolean, default=True)  # 是否启用
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<DocumentType {self.code} - {self.name}>"


class CustomerDocument(Base):
    """客户资料文件表"""
    __tablename__ = "customer_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    document_type_id = Column(String(36), ForeignKey("document_types.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger)
    file_type = Column(String(50))
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    upload_source = Column(String(20))  # mobile, pc, scanner
    status = Column(String(20), default="pending")  # pending, approved, rejected
    reject_reason = Column(Text)
    note = Column(Text)  # 备注
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    
    # 关系
    customer = relationship("Customer", back_populates="documents")
    document_type = relationship("DocumentType")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<CustomerDocument {self.file_name}>"

