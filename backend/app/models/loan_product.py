"""
贷款产品模型
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class LoanProduct(Base):
    """贷款产品表"""
    __tablename__ = "loan_products"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # 关系
    customers = relationship("Customer", back_populates="product")
    document_requirements = relationship("ProductDocumentRequirement", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LoanProduct {self.code} - {self.name}>"


class ProductDocumentRequirement(Base):
    """产品资料清单关联表"""
    __tablename__ = "product_document_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("loan_products.id"), nullable=False)
    document_type_id = Column(String(36), ForeignKey("document_types.id"), nullable=False)
    is_required = Column(Boolean, default=True)
    min_files = Column(Integer, default=1)
    max_files = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)

    # 关系
    product = relationship("LoanProduct", back_populates="document_requirements")
    document_type = relationship("DocumentType")

    def __repr__(self):
        return f"<ProductDocumentRequirement product={self.product_id} doc_type={self.document_type_id}>"

