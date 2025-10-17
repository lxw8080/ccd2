"""
Document API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
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


def validate_file_type(filename: str, allowed_types: str) -> bool:
    """
    Validate file type by checking extension
    For production, consider adding file content validation using python-magic
    """
    # Get file extension
    file_ext = filename.split('.')[-1].lower() if '.' in filename else ''

    # Check if extension is in allowed types
    allowed_extensions = [ext.strip().lower().replace('.', '') for ext in allowed_types.split(',')]

    return file_ext in allowed_extensions


@router.post("/upload", response_model=List[FileUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    customer_id: UUID = Form(...),
    document_type_id: UUID = Form(...),
    files: List[UploadFile] = File(...),
    upload_source: str = Form("web"),
    note: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("document.upload"))
):
    """
    Upload one or more document files
    Supports multiple file upload based on document type configuration
    """
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Check if document type exists and is active
    doc_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )

    if not doc_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document type '{doc_type.name}' is not active"
        )

    # Validate number of files
    num_files = len(files)
    if num_files < doc_type.min_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"At least {doc_type.min_files} file(s) required for {doc_type.name}"
        )

    if num_files > doc_type.max_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {doc_type.max_files} file(s) allowed for {doc_type.name}"
        )

    uploaded_documents = []

    for file in files:
        # Read file content
        content = await file.read()
        file_size = len(content)

        # Validate file size against document type configuration
        max_size = doc_type.max_file_size if doc_type.max_file_size else settings.MAX_FILE_SIZE
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File '{file.filename}' size ({file_size} bytes) exceeds maximum allowed size of {max_size} bytes"
            )

        # Validate file type against document type configuration
        if doc_type.allowed_file_types:
            if not validate_file_type(file.filename, doc_type.allowed_file_types):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{file.filename}' type not allowed. Allowed types: {doc_type.allowed_file_types}"
                )

        # Generate file path with document type code
        file_path = storage_service.generate_file_path(
            file.filename,
            str(customer_id),
            doc_type.code
        )

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
        db.flush()  # Flush to get the ID without committing

        # Get file URL
        file_url = storage_service.get_file_url(file_path)

        uploaded_documents.append(FileUploadResponse(
            file_id=document.id,
            file_name=document.file_name,
            file_size=document.file_size,
            file_url=file_url,
            uploaded_at=document.created_at
        ))

    # Commit all documents at once
    db.commit()

    return uploaded_documents


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


@router.get("/download/{document_id}")
async def download_document(
    document_id: UUID,
    inline: bool = False,  # Add inline parameter for preview
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download a document file

    Args:
        document_id: Document ID
        inline: If True, set Content-Disposition to inline for preview (default: False)
    """
    document = db.query(CustomerDocument).filter(CustomerDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Get local file path
    file_path = storage_service.get_local_file_path(document.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )

    # Determine media type
    media_type = document.file_type or "application/octet-stream"

    # For images and PDFs, default to inline if not specified
    if inline or (media_type and (media_type.startswith('image/') or media_type == 'application/pdf')):
        # Return with inline content disposition for preview
        from fastapi.responses import Response
        import mimetypes
        from urllib.parse import quote

        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()

        # Guess media type if not set
        if not media_type or media_type == "application/octet-stream":
            guessed_type, _ = mimetypes.guess_type(str(file_path))
            if guessed_type:
                media_type = guessed_type

        # Encode filename for Content-Disposition header (RFC 5987)
        # Use both filename and filename* for better compatibility
        encoded_filename = quote(document.file_name)
        # Create ASCII-safe fallback filename
        ascii_filename = document.file_name.encode('ascii', 'ignore').decode('ascii') or 'file'

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'inline; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
                "Cache-Control": "public, max-age=3600",
            }
        )
    else:
        # Return as attachment for download
        return FileResponse(
            path=str(file_path),
            filename=document.file_name,
            media_type=media_type
        )


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


@router.get("/customer/{customer_id}/detailed-completeness")
async def get_detailed_completeness(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed document completeness with all document types and uploaded files
    Returns all active document types with their upload status and file details
    """
    from ..models.document import DocumentType

    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Get all active document types
    document_types = db.query(DocumentType).filter(
        DocumentType.is_active == True
    ).order_by(
        DocumentType.is_required.desc(),
        DocumentType.sort_order,
        DocumentType.name
    ).all()

    # Get all uploaded documents for this customer
    uploaded_docs = db.query(CustomerDocument).filter(
        CustomerDocument.customer_id == customer_id
    ).all()

    # Group documents by type
    docs_by_type = {}
    for doc in uploaded_docs:
        if doc.document_type_id not in docs_by_type:
            docs_by_type[doc.document_type_id] = []
        docs_by_type[doc.document_type_id].append(doc)

    # Build result
    result = {
        "customer_id": str(customer_id),
        "total_required": 0,
        "uploaded_required": 0,
        "approved_required": 0,
        "document_types": []
    }

    for doc_type in document_types:
        documents = docs_by_type.get(doc_type.id, [])

        # Count by status
        pending_count = sum(1 for d in documents if d.status == "pending")
        approved_count = sum(1 for d in documents if d.status == "approved")
        rejected_count = sum(1 for d in documents if d.status == "rejected")

        # Build document list
        doc_list = []
        for doc in documents:
            doc_list.append({
                "id": str(doc.id),
                "file_name": doc.file_name,
                "file_path": doc.file_path,
                "file_size": doc.file_size,
                "file_url": storage_service.get_file_url(doc.file_path),
                "status": doc.status,
                "uploaded_at": doc.created_at.isoformat() if doc.created_at else None,
                "reviewed_at": doc.reviewed_at.isoformat() if doc.reviewed_at else None,
                "review_note": doc.review_note,
                "reject_reason": doc.reject_reason
            })

        # Determine upload status
        upload_status = "not_uploaded"
        if len(documents) > 0:
            if approved_count >= doc_type.min_files:
                upload_status = "approved"
            elif pending_count > 0:
                upload_status = "pending"
            elif rejected_count > 0:
                upload_status = "rejected"
            else:
                upload_status = "uploaded"

        doc_type_info = {
            "id": str(doc_type.id),
            "code": doc_type.code,
            "name": doc_type.name,
            "category": doc_type.category,
            "description": doc_type.description,
            "is_required": doc_type.is_required,
            "min_files": doc_type.min_files,
            "max_files": doc_type.max_files,
            "max_file_size": doc_type.max_file_size,
            "allowed_file_types": doc_type.allowed_file_types,
            "uploaded_count": len(documents),
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "upload_status": upload_status,
            "documents": doc_list
        }

        result["document_types"].append(doc_type_info)

        # Update counters
        if doc_type.is_required:
            result["total_required"] += 1
            if len(documents) >= doc_type.min_files:
                result["uploaded_required"] += 1
            if approved_count >= doc_type.min_files:
                result["approved_required"] += 1

    return result

