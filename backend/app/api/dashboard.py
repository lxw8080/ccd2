"""
Dashboard API Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.customer import Customer
from ..models.loan_product import LoanProduct
from ..models.document import CustomerDocument
from ..models.user import User
from ..core.dependencies import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard statistics
    """
    # Total customers
    total_customers = db.query(func.count(Customer.id)).scalar()
    
    # Total products
    total_products = db.query(func.count(LoanProduct.id)).filter(
        LoanProduct.is_active == True
    ).scalar()
    
    # Customer status breakdown
    pending_customers = db.query(func.count(Customer.id)).filter(
        Customer.status == "pending"
    ).scalar()
    
    collecting_customers = db.query(func.count(Customer.id)).filter(
        Customer.status == "collecting"
    ).scalar()
    
    reviewing_customers = db.query(func.count(Customer.id)).filter(
        Customer.status == "reviewing"
    ).scalar()
    
    completed_customers = db.query(func.count(Customer.id)).filter(
        Customer.status == "completed"
    ).scalar()
    
    # Document statistics
    total_documents = db.query(func.count(CustomerDocument.id)).scalar()
    
    pending_documents = db.query(func.count(CustomerDocument.id)).filter(
        CustomerDocument.status == "pending"
    ).scalar()
    
    approved_documents = db.query(func.count(CustomerDocument.id)).filter(
        CustomerDocument.status == "approved"
    ).scalar()
    
    rejected_documents = db.query(func.count(CustomerDocument.id)).filter(
        CustomerDocument.status == "rejected"
    ).scalar()
    
    return {
        "total_customers": total_customers or 0,
        "total_products": total_products or 0,
        "total_documents": total_documents or 0,
        "pending_customers": pending_customers or 0,
        "collecting_customers": collecting_customers or 0,
        "reviewing_customers": reviewing_customers or 0,
        "completed_customers": completed_customers or 0,
        "pending_documents": pending_documents or 0,
        "approved_documents": approved_documents or 0,
        "rejected_documents": rejected_documents or 0,
    }

