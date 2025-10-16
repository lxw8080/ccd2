"""
Document API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..models.customer import Customer
from ..models.document import CustomerDocument, DocumentType
from ..models.user import User
from ..schemas.document import (
    CustomerDocumentResponse,
    FileUploadResponse,
    DocumentReview,
    CompletenessResult,
)
from ..core.dependencies import get_current_active_user, require_permission
from ..services.storage import storage_service
from ..services.completeness import CompletenessChecker
from ..config import settings


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    customer_id: UUID,
    document_type_id: UUID,
    file: UploadFile = File(...),
    upload_source: str = "web",
    note: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("document.upload"))
):
    """
    Upload a document file
    """
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check if document type exists
    doc_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Generate file path
    file_path = storage_service.generate_file_path(file.filename, str(customer_id))
    
    # Save file
    await file.seek(0)  # Reset file pointer
    await storage_service.save_file(file.file, file_path)
    
    # Create document record
    document = CustomerDocument(
        customer_id=customer_id,
        document_type_id=document_type_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file.content_type or "application/octet-stream",
        upload_source=upload_source,
        uploaded_by=current_user.id,
        note=note
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Get file URL
    file_url = storage_service.get_file_url(file_path)
    
    return FileUploadResponse(
        file_id=document.id,
        file_name=document.file_name,
        file_size=document.file_size,
        file_url=file_url,
        uploaded_at=document.uploaded_at
    )


@router.get("/customer/{customer_id}", response_model=List[CustomerDocumentResponse])
async def list_customer_documents(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all documents for a customer
    """
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get documents
    documents = db.query(CustomerDocument).filter(
        CustomerDocument.customer_id == customer_id
    ).all()
    
    # Add file URLs
    for doc in documents:
        doc.file_url = storage_service.get_file_url(doc.file_path)
    
    return documents


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("document.delete"))
):
    """
    Delete a document
    """
    document = db.query(CustomerDocument).filter(CustomerDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from storage
    await storage_service.delete_file(document.file_path)
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return None


@router.post("/{document_id}/review", response_model=dict)
async def review_document(
    document_id: UUID,
    review_data: DocumentReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("document.review"))
):
    """
    Review a document (approve or reject)
    """
    document = db.query(CustomerDocument).filter(CustomerDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if review_data.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'"
        )
    
    document.status = review_data.status
    document.reviewed_by = current_user.id
    document.review_note = review_data.review_note
    
    db.commit()
    
    return {"message": f"Document {review_data.status} successfully"}


@router.get("/customer/{customer_id}/completeness", response_model=CompletenessResult)
async def check_completeness(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check document completeness for a customer
    """
    checker = CompletenessChecker(db)
    
    try:
        result = checker.check_customer_completeness(customer_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

