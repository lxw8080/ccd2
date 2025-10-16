"""
Loan Product Schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# Document Type Base
class DocumentTypeBase(BaseModel):
    code: str = Field(..., max_length=50, description="Document type code")
    name: str = Field(..., max_length=100, description="Document type name")
    category: Optional[str] = Field(None, max_length=50, description="Category")
    description: Optional[str] = None


class DocumentTypeCreate(DocumentTypeBase):
    pass


class DocumentTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class DocumentTypeResponse(DocumentTypeBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Product Document Requirement
class ProductDocumentRequirementBase(BaseModel):
    document_type_id: UUID
    is_required: bool = True
    min_files: int = Field(1, ge=0, description="Minimum number of files")
    max_files: int = Field(1, ge=1, description="Maximum number of files")
    sort_order: int = Field(0, description="Display order")
    note: Optional[str] = None


class ProductDocumentRequirementCreate(ProductDocumentRequirementBase):
    pass


class ProductDocumentRequirementUpdate(BaseModel):
    is_required: Optional[bool] = None
    min_files: Optional[int] = Field(None, ge=0)
    max_files: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = None
    note: Optional[str] = None


class ProductDocumentRequirementResponse(ProductDocumentRequirementBase):
    id: UUID
    product_id: UUID
    document_type: DocumentTypeResponse

    class Config:
        from_attributes = True


# Loan Product
class LoanProductBase(BaseModel):
    code: str = Field(..., max_length=50, description="Product code")
    name: str = Field(..., max_length=100, description="Product name")
    description: Optional[str] = None
    is_active: bool = True


class LoanProductCreate(LoanProductBase):
    document_requirements: Optional[List[ProductDocumentRequirementCreate]] = []


class LoanProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LoanProductResponse(LoanProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    document_requirements: List[ProductDocumentRequirementResponse] = []

    class Config:
        from_attributes = True


# Simplified response without requirements
class LoanProductSimple(BaseModel):
    id: UUID
    code: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True

