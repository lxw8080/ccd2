"""
Customer Schemas
"""
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field
from uuid import UUID

from .loan_product import LoanProductSimple
from .user import UserResponse


# Customer Base
class CustomerBase(BaseModel):
    customer_no: str = Field(..., max_length=50, description="Customer number")
    name: str = Field(..., max_length=100, description="Customer name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    id_card: Optional[str] = Field(None, max_length=18, description="ID card number")
    email: Optional[str] = Field(None, max_length=100, description="Email")
    address: Optional[str] = Field(None, max_length=500, description="Address")
    product_id: UUID = Field(..., description="Loan product ID")
    status: str = Field("pending", description="Status: pending, in_progress, completed, rejected")
    note: Optional[str] = None


# Create Schema
class CustomerCreate(BaseModel):
    customer_no: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    id_card: Optional[str] = Field(None, max_length=18)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    product_id: UUID
    note: Optional[str] = None


# Update Schema
class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    id_card: Optional[str] = Field(None, max_length=18)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    product_id: Optional[UUID] = None
    status: Optional[str] = None
    note: Optional[str] = None


# Customer Assignment
class CustomerAssignmentBase(BaseModel):
    customer_id: UUID
    user_id: UUID


class CustomerAssignmentCreate(CustomerAssignmentBase):
    pass


class CustomerAssignmentResponse(BaseModel):
    id: UUID
    customer_id: UUID
    user_id: UUID
    assigned_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True


# Response Schema
class CustomerResponse(CustomerBase):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    product: Optional[LoanProductSimple] = None
    assigned_users: List[CustomerAssignmentResponse] = []

    class Config:
        from_attributes = True


# Simple response for list
class CustomerSimple(BaseModel):
    id: UUID
    customer_no: str
    name: str
    phone: Optional[str] = None
    status: str
    product: Optional[LoanProductSimple] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Batch Import Schema
class CustomerImportRow(BaseModel):
    customer_no: str
    name: str
    phone: Optional[str] = None
    id_card: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    product_code: str
    note: Optional[str] = None


class CustomerImportResult(BaseModel):
    total: int
    success: int
    failed: int
    errors: List[dict] = []

