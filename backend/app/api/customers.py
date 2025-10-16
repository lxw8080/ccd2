"""
Customer API Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID

from ..database import get_db
from ..models.customer import Customer, CustomerAssignment
from ..models.user import User
from ..models.loan_product import LoanProduct
from ..schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerSimple,
    CustomerAssignmentCreate,
)
from ..schemas.common import PaginatedResponse
from ..core.dependencies import get_current_active_user, require_permission


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=PaginatedResponse[CustomerSimple])
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    product_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List customers with pagination and filters
    """
    query = db.query(Customer)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Customer.customer_no.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(Customer.status == status)
    
    if product_id:
        query = query.filter(Customer.product_id == product_id)
    
    # For customer_service role, only show assigned customers
    if current_user.role == "customer_service":
        query = query.join(CustomerAssignment).filter(
            CustomerAssignment.user_id == current_user.id
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    customers = query.offset(offset).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": customers,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get customer details
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check permission
    if current_user.role == "customer_service":
        assignment = db.query(CustomerAssignment).filter(
            CustomerAssignment.customer_id == customer_id,
            CustomerAssignment.user_id == current_user.id
        ).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this customer"
            )
    
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer.create"))
):
    """
    Create a new customer
    """
    # Check if customer_no already exists
    existing = db.query(Customer).filter(Customer.customer_no == customer_data.customer_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer number already exists"
        )
    
    # Check if product exists
    product = db.query(LoanProduct).filter(LoanProduct.id == customer_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Create customer
    customer = Customer(
        **customer_data.model_dump(),
        created_by=current_user.id
    )
    db.add(customer)
    db.flush()
    
    # Auto-assign to creator if customer_service
    if current_user.role == "customer_service":
        assignment = CustomerAssignment(
            customer_id=customer.id,
            user_id=current_user.id
        )
        db.add(assignment)
    
    db.commit()
    db.refresh(customer)
    
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer.update"))
):
    """
    Update customer information
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check permission for customer_service
    if current_user.role == "customer_service":
        assignment = db.query(CustomerAssignment).filter(
            CustomerAssignment.customer_id == customer_id,
            CustomerAssignment.user_id == current_user.id
        ).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this customer"
            )
    
    # Update fields
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer.delete"))
):
    """
    Delete a customer
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    db.delete(customer)
    db.commit()
    
    return None


# Customer Assignment
@router.post("/{customer_id}/assign", status_code=status.HTTP_201_CREATED)
async def assign_customer(
    customer_id: UUID,
    assignment_data: CustomerAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer.assign"))
):
    """
    Assign a customer to a user
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    user = db.query(User).filter(User.id == assignment_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already assigned
    existing = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == customer_id,
        CustomerAssignment.user_id == assignment_data.user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already assigned to this user"
        )
    
    assignment = CustomerAssignment(
        customer_id=customer_id,
        user_id=assignment_data.user_id
    )
    db.add(assignment)
    db.commit()
    
    return {"message": "Customer assigned successfully"}


@router.delete("/{customer_id}/assign/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_customer(
    customer_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("customer.assign"))
):
    """
    Unassign a customer from a user
    """
    assignment = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == customer_id,
        CustomerAssignment.user_id == user_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    db.delete(assignment)
    db.commit()
    
    return None

