"""
Loan Product API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..models.loan_product import LoanProduct, ProductDocumentRequirement
from ..models.document import DocumentType
from ..models.user import User
from ..schemas.loan_product import (
    LoanProductCreate,
    LoanProductUpdate,
    LoanProductResponse,
    LoanProductSimple,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentTypeResponse,
    ProductDocumentRequirementCreate,
    ProductDocumentRequirementUpdate,
)
from ..core.dependencies import get_current_active_user, require_permission


router = APIRouter(prefix="/products", tags=["Loan Products"])


# Document Types
@router.get("/document-types", response_model=List[DocumentTypeResponse])
async def list_document_types(
    is_active: bool = None,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all document types with optional filters
    所有登录用户都可以查看资料类型列表
    """
    query = db.query(DocumentType).order_by(DocumentType.sort_order, DocumentType.name)

    if is_active is not None:
        query = query.filter(DocumentType.is_active == is_active)

    if category:
        query = query.filter(DocumentType.category == category)

    document_types = query.all()
    return document_types


@router.get("/document-types/{document_type_id}", response_model=DocumentTypeResponse)
async def get_document_type(
    document_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific document type by ID
    """
    document_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not document_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )
    return document_type


@router.post("/document-types", response_model=DocumentTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_document_type(
    document_type_data: DocumentTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Create a new document type
    """
    # Check if code already exists
    existing = db.query(DocumentType).filter(DocumentType.code == document_type_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document type code already exists"
        )

    document_type = DocumentType(**document_type_data.model_dump())
    db.add(document_type)
    db.commit()
    db.refresh(document_type)

    return document_type


@router.put("/document-types/{document_type_id}", response_model=DocumentTypeResponse)
async def update_document_type(
    document_type_id: UUID,
    document_type_data: DocumentTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Update a document type
    """
    document_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not document_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )

    # Update fields
    update_data = document_type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document_type, field, value)

    db.commit()
    db.refresh(document_type)

    return document_type


@router.delete("/document-types/{document_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_type(
    document_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Delete a document type
    """
    document_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not document_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )

    # Check if document type is being used
    from ..models.document import CustomerDocument
    existing_docs = db.query(CustomerDocument).filter(
        CustomerDocument.document_type_id == document_type_id
    ).first()

    if existing_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete document type that is being used by customer documents"
        )

    db.delete(document_type)
    db.commit()

    return None


# Loan Products
@router.get("/", response_model=List[LoanProductSimple])
async def list_products(
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all loan products
    """
    query = db.query(LoanProduct)
    if is_active is not None:
        query = query.filter(LoanProduct.is_active == is_active)
    
    products = query.all()
    return products


@router.get("/{product_id}", response_model=LoanProductResponse)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get product details with document requirements
    """
    product = db.query(LoanProduct).filter(LoanProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.post("/", response_model=LoanProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: LoanProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Create a new loan product
    """
    # Check if code already exists
    existing = db.query(LoanProduct).filter(LoanProduct.code == product_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists"
        )
    
    # Create product
    product_dict = product_data.model_dump(exclude={"document_requirements"})
    product = LoanProduct(**product_dict)
    db.add(product)
    db.flush()
    
    # Add document requirements
    if product_data.document_requirements:
        for req_data in product_data.document_requirements:
            requirement = ProductDocumentRequirement(
                product_id=product.id,
                **req_data.model_dump()
            )
            db.add(requirement)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.put("/{product_id}", response_model=LoanProductResponse)
async def update_product(
    product_id: UUID,
    product_data: LoanProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Update a loan product
    """
    product = db.query(LoanProduct).filter(LoanProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Delete a loan product
    """
    product = db.query(LoanProduct).filter(LoanProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return None


# Product Document Requirements
@router.post("/{product_id}/requirements", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_document_requirement(
    product_id: UUID,
    requirement_data: ProductDocumentRequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Add a document requirement to a product
    """
    product = db.query(LoanProduct).filter(LoanProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if document type exists
    doc_type = db.query(DocumentType).filter(
        DocumentType.id == requirement_data.document_type_id
    ).first()
    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )
    
    # Check if requirement already exists
    existing = db.query(ProductDocumentRequirement).filter(
        ProductDocumentRequirement.product_id == product_id,
        ProductDocumentRequirement.document_type_id == requirement_data.document_type_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document requirement already exists for this product"
        )
    
    requirement = ProductDocumentRequirement(
        product_id=product_id,
        **requirement_data.model_dump()
    )
    db.add(requirement)
    db.commit()
    
    return {"message": "Document requirement added successfully"}


@router.delete("/{product_id}/requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document_requirement(
    product_id: UUID,
    requirement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("product.manage"))
):
    """
    Remove a document requirement from a product
    """
    requirement = db.query(ProductDocumentRequirement).filter(
        ProductDocumentRequirement.id == requirement_id,
        ProductDocumentRequirement.product_id == product_id
    ).first()
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document requirement not found"
        )
    
    db.delete(requirement)
    db.commit()
    
    return None

