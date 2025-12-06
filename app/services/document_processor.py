"""
Document processor service using LangChain and Gemini.

Handles extraction of financial data from various document types.
"""

import json
import base64
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.ai.gemini_client import gemini_client
from app.models.financial_data import FinancialData, DataSource, ProcessingStatus


class DocumentProcessor:
    """
    Document processor for extracting financial data.
    
    Uses LangChain document loaders and Gemini for
    intelligent extraction from various document types.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize document processor."""
        self.db = db
        self.gemini = gemini_client
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200
        )
    
    async def process_document(
        self,
        user_id: int,
        file_content: bytes,
        filename: str,
        mime_type: str,
        document_type: str = "auto"
    ) -> FinancialData:
        """
        Process an uploaded document and extract financial data.
        
        Args:
            user_id: ID of the user uploading the document
            file_content: Raw file bytes
            filename: Original filename
            mime_type: MIME type of the file
            document_type: Type of document (auto-detected if 'auto')
            
        Returns:
            FinancialData record with extracted information
        """
        # Create initial record
        financial_data = FinancialData(
            user_id=user_id,
            source=self._detect_source(document_type, filename),
            source_identifier=filename,
            processing_status=ProcessingStatus.PROCESSING,
            data_json="{}",
            extraction_method="langchain"
        )
        self.db.add(financial_data)
        await self.db.commit()
        
        try:
            # Auto-detect document type if needed
            if document_type == "auto":
                document_type = self._auto_detect_type(filename, mime_type)
            
            # Process based on mime type
            if mime_type == "application/pdf":
                extracted = await self._process_pdf(file_content, document_type)
            elif mime_type.startswith("image/"):
                extracted = await self._process_image(file_content, document_type, mime_type)
            else:
                extracted = await self._process_text(file_content, document_type)
            
            # Update record with results
            financial_data.data_json = json.dumps(extracted.get("data", {}))
            financial_data.summary = extracted.get("summary", "")
            financial_data.confidence_score = extracted.get("confidence_score", 0)
            financial_data.processing_status = ProcessingStatus.COMPLETED
            
        except Exception as e:
            financial_data.processing_status = ProcessingStatus.FAILED
            financial_data.error_message = str(e)
            financial_data.confidence_score = 0
        
        await self.db.commit()
        await self.db.refresh(financial_data)
        
        return financial_data
    
    async def process_image_document(
        self,
        user_id: int,
        image_data: Union[bytes, str],
        document_type: str,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Process an image document using Gemini Vision.
        
        Args:
            user_id: User ID
            image_data: Image bytes or base64 string
            document_type: Type of document
            mime_type: Image MIME type
            
        Returns:
            Extracted financial data
        """
        # Use Gemini for image processing
        extracted = await self.gemini.extract_financial_data_from_image(
            image_data=image_data,
            document_type=document_type,
            mime_type=mime_type
        )
        
        # Store in database
        financial_data = FinancialData(
            user_id=user_id,
            source=self._detect_source(document_type, "image"),
            source_identifier=f"image_{datetime.utcnow().isoformat()}",
            data_json=json.dumps(extracted),
            processing_status=ProcessingStatus.COMPLETED,
            confidence_score=extracted.get("confidence_score", 75),
            extraction_method="gemini"
        )
        self.db.add(financial_data)
        await self.db.commit()
        
        return {
            "id": financial_data.id,
            "data": extracted,
            "confidence_score": financial_data.confidence_score,
            "processing_status": financial_data.processing_status.value
        }
    
    async def _process_pdf(
        self,
        file_content: bytes,
        document_type: str
    ) -> Dict[str, Any]:
        """Process a PDF document."""
        import tempfile
        import os
        
        # Save to temp file for PyPDFLoader
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        try:
            # Load and split document
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            
            # Combine text
            full_text = "\n".join(doc.page_content for doc in documents)
            
            # Extract using Gemini
            extracted = await self._extract_with_ai(full_text, document_type)
            
            return extracted
            
        finally:
            os.unlink(tmp_path)
    
    async def _process_image(
        self,
        file_content: bytes,
        document_type: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """Process an image document using Gemini Vision."""
        extracted = await self.gemini.extract_financial_data_from_image(
            image_data=file_content,
            document_type=document_type,
            mime_type=mime_type
        )
        
        # Generate summary
        summary = await self.gemini.summarize_financial_document(
            json.dumps(extracted),
            document_type
        )
        
        return {
            "data": extracted,
            "summary": summary.get("summary", ""),
            "confidence_score": extracted.get("confidence_score", 75)
        }
    
    async def _process_text(
        self,
        file_content: bytes,
        document_type: str
    ) -> Dict[str, Any]:
        """Process a text document."""
        text = file_content.decode("utf-8", errors="ignore")
        return await self._extract_with_ai(text, document_type)
    
    async def _extract_with_ai(
        self,
        text: str,
        document_type: str
    ) -> Dict[str, Any]:
        """Extract structured data from text using AI."""
        # Split if too long
        chunks = self.text_splitter.split_text(text) if len(text) > 4000 else [text]
        
        all_data = {}
        
        for chunk in chunks:
            prompt = f"""Extract financial information from this {document_type} text.

Text:
{chunk}

Return JSON with relevant financial data including:
- Any amounts, dates, account numbers
- Transaction details if present
- Names, references, identifiers
- Key financial metrics

Format as structured JSON."""
            
            try:
                extracted = await self.gemini.generate_json(prompt)
                # Merge results
                for key, value in extracted.items():
                    if key not in all_data:
                        all_data[key] = value
                    elif isinstance(value, list):
                        all_data[key] = all_data.get(key, []) + value
            except Exception:
                continue
        
        # Generate summary
        summary_result = await self.gemini.summarize_financial_document(
            text[:2000],
            document_type
        )
        
        return {
            "data": all_data,
            "summary": summary_result.get("summary", ""),
            "confidence_score": 70
        }
    
    def _detect_source(self, document_type: str, filename: str) -> DataSource:
        """Detect the data source type."""
        type_mapping = {
            "bank_statement": DataSource.BANK_STATEMENT,
            "pay_stub": DataSource.PAY_STUB,
            "tax_document": DataSource.TAX_DOCUMENT,
            "receipt": DataSource.DOCUMENT_UPLOAD,
        }
        
        # Check document type
        if document_type in type_mapping:
            return type_mapping[document_type]
        
        # Check filename
        filename_lower = filename.lower()
        if "bank" in filename_lower or "statement" in filename_lower:
            return DataSource.BANK_STATEMENT
        elif "pay" in filename_lower or "salary" in filename_lower:
            return DataSource.PAY_STUB
        elif "tax" in filename_lower:
            return DataSource.TAX_DOCUMENT
        
        return DataSource.DOCUMENT_UPLOAD
    
    def _auto_detect_type(self, filename: str, mime_type: str) -> str:
        """Auto-detect document type from filename."""
        filename_lower = filename.lower()
        
        if "bank" in filename_lower or "statement" in filename_lower:
            return "bank_statement"
        elif "pay" in filename_lower or "salary" in filename_lower or "slip" in filename_lower:
            return "pay_stub"
        elif "receipt" in filename_lower or "invoice" in filename_lower:
            return "receipt"
        elif "tax" in filename_lower:
            return "tax_document"
        
        return "general"
    
    async def get_user_documents(
        self,
        user_id: int,
        source: Optional[DataSource] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[FinancialData], int]:
        """Get user's processed documents."""
        from sqlalchemy import select, func
        
        query = select(FinancialData).where(FinancialData.user_id == user_id)
        
        if source:
            query = query.where(FinancialData.source == source)
        
        # Count
        count_query = select(func.count(FinancialData.id)).where(
            FinancialData.user_id == user_id
        )
        if source:
            count_query = count_query.where(FinancialData.source == source)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Paginate
        query = query.order_by(FinancialData.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        documents = result.scalars().all()
        
        return list(documents), total

