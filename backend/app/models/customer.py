"""
客户模型
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Customer(Base):
    """客户表"""
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_no = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), index=True)
    id_card = Column(String(18), index=True)
    email = Column(String(100), index=True)
    address = Column(String(500))
    product_id = Column(UUID(as_uuid=True), ForeignKey("loan_products.id"))
    status = Column(String(20), default="collecting", index=True)
    note = Column(String(500))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    product = relationship("LoanProduct", back_populates="customers")
    documents = relationship("CustomerDocument", back_populates="customer", cascade="all, delete-orphan")
    assignments = relationship("CustomerAssignment", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer {self.customer_no} - {self.name}>"


class CustomerAssignment(Base):
    """客户分配表"""
    __tablename__ = "customer_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    customer = relationship("Customer", back_populates="assignments")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CustomerAssignment customer={self.customer_id} user={self.user_id}>"

