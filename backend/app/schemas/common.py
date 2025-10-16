"""
Common Schemas
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field


T = TypeVar('T')


# Paginated Response
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# API Response
class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


# Error Response
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None
    error_code: Optional[str] = None


# Audit Log Schema
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    customer_id: Optional[str] = None
    action: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

