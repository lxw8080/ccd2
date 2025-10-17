"""
Document Schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, computed_field
from uuid import UUID


# Customer Document Base
class CustomerDocumentBase(BaseModel):
    customer_id: UUID
    document_type_id: UUID
    file_name: str = Field(..., max_length=255)
    file_size: int = Field(..., ge=0, description="File size in bytes")
    file_type: str = Field(..., max_length=50, description="MIME type")
    upload_source: str = Field("web", description="Upload source: web, mobile, scanner")
    note: Optional[str] = None


# Create Schema
class CustomerDocumentCreate(BaseModel):
    customer_id: UUID
    document_type_id: UUID
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    upload_source: str = "web"
    note: Optional[str] = None


# Update Schema
class CustomerDocumentUpdate(BaseModel):
    document_type_id: Optional[UUID] = None
    note: Optional[str] = None
    status: Optional[str] = None


# Response Schema
class CustomerDocumentResponse(CustomerDocumentBase):
    id: UUID
    file_path: str
    file_url: Optional[str] = None  # Signed URL for download
    status: str
    uploaded_by: Optional[UUID] = None
    created_at: datetime  # Database field - represents upload time
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_note: Optional[str] = None

    class Config:
        from_attributes = True

    @computed_field  # type: ignore[misc]
    @property
    def uploaded_at(self) -> datetime:
        """Computed field: alias for created_at to maintain API compatibility"""
        return self.created_at


# File Upload Response
class FileUploadResponse(BaseModel):
    file_id: UUID
    file_name: str
    file_size: int
    file_url: str
    uploaded_at: datetime


# Document Review Schema
class DocumentReview(BaseModel):
    status: str = Field(..., description="approved or rejected")
    review_note: Optional[str] = None


# Completeness Check Result
class DocumentRequirementStatus(BaseModel):
    document_type_id: UUID
    document_type_code: str
    document_type_name: str
    is_required: bool
    min_files: int
    max_files: int
    uploaded_count: int
    is_satisfied: bool
    missing_count: int


class CompletenessResult(BaseModel):
    customer_id: UUID
    product_id: UUID
    total_requirements: int
    satisfied_requirements: int
    missing_requirements: int
    completion_percentage: float
    is_complete: bool
    requirements: List[DocumentRequirementStatus]

