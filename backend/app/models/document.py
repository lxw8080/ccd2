"""
文档模型
"""
from sqlalchemy import Column, String, Boolean, Integer, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class DocumentType(Base):
    """资料类型表"""
    __tablename__ = "document_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # identity, financial, credit, other
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DocumentType {self.code} - {self.name}>"


class CustomerDocument(Base):
    """客户资料文件表"""
    __tablename__ = "customer_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    document_type_id = Column(UUID(as_uuid=True), ForeignKey("document_types.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger)
    file_type = Column(String(50))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    upload_source = Column(String(20))  # mobile, pc, scanner
    status = Column(String(20), default="pending")  # pending, approved, rejected
    reject_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    customer = relationship("Customer", back_populates="documents")
    document_type = relationship("DocumentType")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<CustomerDocument {self.file_name}>"

