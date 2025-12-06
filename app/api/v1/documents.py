"""
Document processing API endpoints.

Provides endpoints for uploading and processing financial documents.
"""

import base64
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.session import get_async_session
from app.models.user import User
from app.models.financial_data import DataSource, ProcessingStatus
from app.services.document_processor import DocumentProcessor
from app.services.email_parser import EmailParser
from app.mcp.mcp_client import mcp_client
from app.utils.security import get_current_user

router = APIRouter()


# Pydantic schemas for this endpoint
class DocumentResponse(BaseModel):
    """Response for document operations."""
    id: int
    source: str
    source_identifier: Optional[str]
    processing_status: str
    confidence_score: int
    summary: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class ExtractRequest(BaseModel):
    """Request for data extraction."""
    content: str
    content_type: str = "text"
    extraction_type: str = "general"


class EmailSyncRequest(BaseModel):
    """Request for email sync."""
    days: int = 30


@router.post(
    "/upload",
    response_model=DocumentResponse,
    summary="Upload financial document",
    description="Upload a financial document for processing and data extraction."
)
async def upload_document(
    file: UploadFile = File(..., description="Document file (PDF, image)"),
    document_type: str = Query("auto", description="Document type (auto, bank_statement, pay_stub, receipt)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> DocumentResponse:
    """
    Upload and process a financial document.
    
    Supported formats:
    - PDF documents
    - Images (JPEG, PNG)
    - Text files
    
    The document will be analyzed using AI to extract:
    - Transaction details
    - Account information
    - Amounts and dates
    - Other financial data
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Determine MIME type
    mime_type = file.content_type or "application/octet-stream"
    
    # Validate MIME type
    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
        "text/plain"
    ]
    if mime_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {mime_type}"
        )
    
    # Process document
    processor = DocumentProcessor(db)
    
    try:
        result = await processor.process_document(
            user_id=current_user.id,
            file_content=content,
            filename=file.filename,
            mime_type=mime_type,
            document_type=document_type
        )
        
        return DocumentResponse(
            id=result.id,
            source=result.source.value,
            source_identifier=result.source_identifier,
            processing_status=result.processing_status.value,
            confidence_score=result.confidence_score,
            summary=result.summary,
            created_at=result.created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )


@router.post(
    "/extract",
    summary="Extract data from content",
    description="Extract financial data from text or base64 encoded content."
)
async def extract_data(
    request: ExtractRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Extract financial data from provided content.
    
    - **content**: Text content or base64 encoded image
    - **content_type**: Type of content (text, image)
    - **extraction_type**: Type of document (bank_statement, pay_stub, receipt, general)
    
    Uses AI to intelligently extract:
    - Amounts and currencies
    - Dates and periods
    - Transaction details
    - Account information
    """
    processor = DocumentProcessor(db)
    
    try:
        if request.content_type == "image":
            # Decode base64 image
            try:
                image_data = base64.b64decode(request.content)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid base64 image data"
                )
            
            result = await processor.process_image_document(
                user_id=current_user.id,
                image_data=image_data,
                document_type=request.extraction_type
            )
        else:
            # Process text content
            result = await processor.process_document(
                user_id=current_user.id,
                file_content=request.content.encode(),
                filename="text_extraction.txt",
                mime_type="text/plain",
                document_type=request.extraction_type
            )
            result = {
                "id": result.id,
                "data": result.get_data(),
                "confidence_score": result.confidence_score,
                "processing_status": result.processing_status.value
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )


@router.get(
    "",
    summary="List processed documents",
    description="Get list of processed documents for the current user."
)
async def list_documents(
    source: Optional[str] = Query(None, description="Filter by source type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    List all processed documents for the current user.
    
    Supports filtering by source type and pagination.
    """
    processor = DocumentProcessor(db)
    
    # Convert source string to enum
    source_enum = None
    if source:
        try:
            source_enum = DataSource(source)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source type: {source}"
            )
    
    documents, total = await processor.get_user_documents(
        user_id=current_user.id,
        source=source_enum,
        page=page,
        page_size=page_size
    )
    
    return {
        "items": [
            DocumentResponse(
                id=doc.id,
                source=doc.source.value,
                source_identifier=doc.source_identifier,
                processing_status=doc.processing_status.value,
                confidence_score=doc.confidence_score,
                summary=doc.summary,
                created_at=doc.created_at.isoformat()
            )
            for doc in documents
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get(
    "/{document_id}",
    summary="Get document details",
    description="Get detailed information about a processed document."
)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """Get details of a specific document including extracted data."""
    from sqlalchemy import select
    from app.models.financial_data import FinancialData
    
    result = await db.execute(
        select(FinancialData).where(
            FinancialData.id == document_id,
            FinancialData.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "id": document.id,
        "source": document.source.value,
        "source_identifier": document.source_identifier,
        "processing_status": document.processing_status.value,
        "confidence_score": document.confidence_score,
        "summary": document.summary,
        "data": document.get_data(),
        "is_verified": document.is_verified,
        "extraction_method": document.extraction_method,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat()
    }


@router.post(
    "/email/sync",
    summary="Sync financial emails",
    description="Synchronize and process financial emails from connected email account."
)
async def sync_emails(
    request: EmailSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Sync financial emails from connected email account.
    
    Fetches emails from the last N days and extracts financial information.
    Supports Gmail API integration.
    
    - **days**: Number of days to look back (default: 30)
    """
    parser = EmailParser(db)
    
    # Try to initialize Gmail (will use mock data if not configured)
    await parser.initialize_gmail()
    
    result = await parser.sync_financial_emails(
        user_id=current_user.id,
        days=request.days
    )
    
    return result


@router.post(
    "/mcp/process",
    summary="Process via MCP",
    description="Process content using MCP (Model Context Protocol) tools."
)
async def process_via_mcp(
    request: ExtractRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Process content using MCP protocol.
    
    Uses MCP tools for financial data extraction.
    Falls back to standard processing if MCP is unavailable.
    """
    if not mcp_client.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service is not available"
        )
    
    try:
        # Connect to MCP server
        connected = await mcp_client.connect()
        if not connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to MCP server"
            )
        
        # Call extraction tool
        result = await mcp_client.extract_financial_data(
            content=request.content,
            content_type=request.content_type,
            extraction_type=request.extraction_type
        )
        
        # Disconnect
        await mcp_client.disconnect()
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MCP processing failed: {str(e)}"
        )

