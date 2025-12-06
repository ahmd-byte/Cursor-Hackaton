"""
Financial data model for storing extracted financial information.
"""

from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Enum,
    Text,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship, Mapped
import enum

from app.database.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class DataSource(str, enum.Enum):
    """Sources of financial data."""
    
    BANK_STATEMENT = "bank_statement"
    PAY_STUB = "pay_stub"
    TAX_DOCUMENT = "tax_document"
    CREDIT_REPORT = "credit_report"
    EMAIL_TRANSACTION = "email_transaction"
    MANUAL_ENTRY = "manual_entry"
    PLAID_SYNC = "plaid_sync"
    EMPLOYER_PAYROLL = "employer_payroll"
    DOCUMENT_UPLOAD = "document_upload"


class ProcessingStatus(str, enum.Enum):
    """Status of data processing."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class FinancialData(BaseModel):
    """
    Financial data model for storing extracted financial information.
    
    This model stores financial data extracted from various sources
    like bank statements, emails, and uploaded documents.
    
    Attributes:
        user_id: Reference to the owning user
        source: Source of the financial data
        source_identifier: Unique identifier for the source document
        data_json: JSON string containing extracted financial data
        summary: AI-generated summary of the financial data
        processing_status: Current processing status
        confidence_score: AI confidence in extraction accuracy (0-100)
        raw_content: Original raw content (for reprocessing)
    """
    
    __tablename__ = "financial_data"
    
    # Foreign key to user
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the owning user"
    )
    
    # Source information
    source = Column(
        Enum(DataSource),
        nullable=False,
        index=True,
        doc="Source of the financial data"
    )
    source_identifier = Column(
        String(255),
        nullable=True,
        doc="Unique identifier for the source (filename, email ID, etc.)"
    )
    source_url = Column(
        Text,
        nullable=True,
        doc="URL or path to the original source"
    )
    
    # Extracted data
    data_json = Column(
        Text,
        nullable=False,
        doc="JSON string containing extracted financial data"
    )
    summary = Column(
        Text,
        nullable=True,
        doc="AI-generated summary of the financial data"
    )
    
    # Processing information
    processing_status = Column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        nullable=False,
        index=True,
        doc="Current processing status"
    )
    confidence_score = Column(
        Integer,
        default=0,
        nullable=False,
        doc="AI confidence in extraction accuracy (0-100)"
    )
    error_message = Column(
        Text,
        nullable=True,
        doc="Error message if processing failed"
    )
    
    # Original content (for reprocessing)
    raw_content = Column(
        Text,
        nullable=True,
        doc="Original raw content for reprocessing"
    )
    
    # Flags
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the extracted data has been verified by user"
    )
    is_used_for_analysis = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this data should be used for AI analysis"
    )
    
    # MCP-related fields
    mcp_session_id = Column(
        String(100),
        nullable=True,
        doc="MCP session ID if extracted via MCP"
    )
    extraction_method = Column(
        String(50),
        default="langchain",
        nullable=False,
        doc="Method used for extraction (langchain, mcp, gemini)"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="financial_data"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_financial_data_user_source", "user_id", "source"),
        Index("ix_financial_data_user_status", "user_id", "processing_status"),
    )
    
    def __repr__(self) -> str:
        return f"<FinancialData(id={self.id}, source={self.source}, user_id={self.user_id})>"
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if extraction confidence is high (>= 80%)."""
        return self.confidence_score >= 80
    
    @property
    def needs_review(self) -> bool:
        """Check if this data needs manual review."""
        return (
            not self.is_verified and
            (self.confidence_score < 70 or self.processing_status == ProcessingStatus.PARTIAL)
        )
    
    def get_data(self) -> dict:
        """Parse and return the JSON data."""
        import json
        if self.data_json:
            return json.loads(self.data_json)
        return {}
    
    def set_data(self, data: dict) -> None:
        """Set the JSON data from a dictionary."""
        import json
        self.data_json = json.dumps(data)

