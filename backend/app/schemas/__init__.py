"""
Pydantic Schemas Module
"""
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenData,
    PasswordChange,
)
from .loan_product import (
    DocumentTypeBase,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentTypeResponse,
    ProductDocumentRequirementBase,
    ProductDocumentRequirementCreate,
    ProductDocumentRequirementUpdate,
    ProductDocumentRequirementResponse,
    LoanProductBase,
    LoanProductCreate,
    LoanProductUpdate,
    LoanProductResponse,
    LoanProductSimple,
)
from .customer import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerSimple,
    CustomerAssignmentCreate,
    CustomerAssignmentResponse,
    CustomerImportRow,
    CustomerImportResult,
)
from .document import (
    CustomerDocumentBase,
    CustomerDocumentCreate,
    CustomerDocumentUpdate,
    CustomerDocumentResponse,
    FileUploadResponse,
    DocumentReview,
    DocumentRequirementStatus,
    CompletenessResult,
)
from .common import (
    PaginatedResponse,
    ApiResponse,
    ErrorResponse,
    AuditLogResponse,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    "PasswordChange",
    # Loan Product
    "DocumentTypeBase",
    "DocumentTypeCreate",
    "DocumentTypeUpdate",
    "DocumentTypeResponse",
    "ProductDocumentRequirementBase",
    "ProductDocumentRequirementCreate",
    "ProductDocumentRequirementUpdate",
    "ProductDocumentRequirementResponse",
    "LoanProductBase",
    "LoanProductCreate",
    "LoanProductUpdate",
    "LoanProductResponse",
    "LoanProductSimple",
    # Customer
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerSimple",
    "CustomerAssignmentCreate",
    "CustomerAssignmentResponse",
    "CustomerImportRow",
    "CustomerImportResult",
    # Document
    "CustomerDocumentBase",
    "CustomerDocumentCreate",
    "CustomerDocumentUpdate",
    "CustomerDocumentResponse",
    "FileUploadResponse",
    "DocumentReview",
    "DocumentRequirementStatus",
    "CompletenessResult",
    # Common
    "PaginatedResponse",
    "ApiResponse",
    "ErrorResponse",
    "AuditLogResponse",
]

