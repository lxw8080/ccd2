"""
数据库模型
"""
from app.models.user import User
from app.models.customer import Customer, CustomerAssignment
from app.models.loan_product import LoanProduct, ProductDocumentRequirement
from app.models.document import DocumentType, CustomerDocument
from app.models.audit_log import AuditLog
from app.models.import_record import ImportRecord

__all__ = [
    "User",
    "Customer",
    "CustomerAssignment",
    "LoanProduct",
    "ProductDocumentRequirement",
    "DocumentType",
    "CustomerDocument",
    "AuditLog",
    "ImportRecord",
]

