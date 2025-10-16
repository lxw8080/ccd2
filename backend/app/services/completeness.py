"""
Document Completeness Checker Service
"""
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID

from ..models.customer import Customer
from ..models.loan_product import ProductDocumentRequirement
from ..models.document import CustomerDocument
from ..schemas.document import CompletenessResult, DocumentRequirementStatus


class CompletenessChecker:
    """
    Service to check if customer documents are complete
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_customer_completeness(self, customer_id: UUID) -> CompletenessResult:
        """
        Check if a customer's documents are complete
        """
        # Get customer
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        
        # Get product requirements
        requirements = self.db.query(ProductDocumentRequirement).filter(
            ProductDocumentRequirement.product_id == customer.product_id
        ).all()
        
        # Get uploaded documents
        uploaded_docs = self.db.query(CustomerDocument).filter(
            CustomerDocument.customer_id == customer_id,
            CustomerDocument.status.in_(["pending", "approved"])
        ).all()
        
        # Group uploaded documents by type
        docs_by_type = {}
        for doc in uploaded_docs:
            if doc.document_type_id not in docs_by_type:
                docs_by_type[doc.document_type_id] = []
            docs_by_type[doc.document_type_id].append(doc)
        
        # Check each requirement
        requirement_statuses: List[DocumentRequirementStatus] = []
        satisfied_count = 0
        missing_count = 0
        
        for req in requirements:
            uploaded_count = len(docs_by_type.get(req.document_type_id, []))
            
            # Check if requirement is satisfied
            is_satisfied = True
            missing = 0
            
            if req.is_required:
                if uploaded_count < req.min_files:
                    is_satisfied = False
                    missing = req.min_files - uploaded_count
            
            if is_satisfied:
                satisfied_count += 1
            else:
                missing_count += 1
            
            requirement_statuses.append(
                DocumentRequirementStatus(
                    document_type_id=req.document_type_id,
                    document_type_code=req.document_type.code,
                    document_type_name=req.document_type.name,
                    is_required=req.is_required,
                    min_files=req.min_files,
                    max_files=req.max_files,
                    uploaded_count=uploaded_count,
                    is_satisfied=is_satisfied,
                    missing_count=missing
                )
            )
        
        total_requirements = len(requirements)
        completion_percentage = (satisfied_count / total_requirements * 100) if total_requirements > 0 else 0
        is_complete = missing_count == 0
        
        return CompletenessResult(
            customer_id=customer_id,
            product_id=customer.product_id,
            total_requirements=total_requirements,
            satisfied_requirements=satisfied_count,
            missing_requirements=missing_count,
            completion_percentage=round(completion_percentage, 2),
            is_complete=is_complete,
            requirements=requirement_statuses
        )
    
    def get_missing_documents(self, customer_id: UUID) -> List[DocumentRequirementStatus]:
        """
        Get list of missing documents for a customer
        """
        result = self.check_customer_completeness(customer_id)
        return [req for req in result.requirements if not req.is_satisfied]

