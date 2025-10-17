"""
Loan Product Schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Document Type Base
class DocumentTypeBase(BaseModel):
    code: str = Field(..., max_length=50, description="Document type code")
    name: str = Field(..., max_length=100, description="Document type name")
    category: Optional[str] = Field(None, max_length=50, description="Category: identity, financial, credit, other")
    description: Optional[str] = None
    is_required: bool = Field(False, description="是否必须上传")
    allowed_file_types: Optional[str] = Field(None, description="允许的文件类型，逗号分隔，如：jpg,png,pdf")
    max_file_size: int = Field(10485760, description="最大文件大小（字节），默认10MB")
    min_files: int = Field(1, ge=1, description="最少文件数量")
    max_files: int = Field(1, ge=1, description="最多文件数量")
    is_active: bool = Field(True, description="是否启用")
    sort_order: int = Field(0, description="排序顺序")


class DocumentTypeCreate(DocumentTypeBase):
    pass


class DocumentTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_required: Optional[bool] = None
    allowed_file_types: Optional[str] = None
    max_file_size: Optional[int] = Field(None, ge=1)
    min_files: Optional[int] = Field(None, ge=1)
    max_files: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class DocumentTypeResponse(DocumentTypeBase):
    id: str = Field(..., description="Document type ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product Document Requirement
class ProductDocumentRequirementBase(BaseModel):
    document_type_id: str = Field(..., description="Document type ID")
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
    id: str = Field(..., description="Requirement ID")
    product_id: str = Field(..., description="Product ID")
    document_type: Optional[DocumentTypeResponse] = None

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
    id: str = Field(..., description="Product ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    document_requirements: List[ProductDocumentRequirementResponse] = []

    class Config:
        from_attributes = True


# Simplified response without requirements
class LoanProductSimple(BaseModel):
    id: str = Field(..., description="Product ID")
    code: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True
