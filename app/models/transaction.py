"""
Transaction model for tracking all financial movements.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    Column,
    String,
    Numeric,
    Integer,
    ForeignKey,
    Enum,
    Text,
    Index,
)
from sqlalchemy.orm import relationship, Mapped
import enum

from app.database.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.bucket import Bucket


class TransactionType(str, enum.Enum):
    """Types of transactions."""
    
    # Wage-related
    WAGE_ADVANCE = "wage_advance"
    WAGE_REPAYMENT = "wage_repayment"
    SALARY_CREDIT = "salary_credit"
    
    # Bucket-related
    BUCKET_DEPOSIT = "bucket_deposit"
    BUCKET_WITHDRAWAL = "bucket_withdrawal"
    BUCKET_TRANSFER = "bucket_transfer"
    
    # AI-related
    AUTO_ALLOCATION = "auto_allocation"
    
    # General
    MANUAL_ADJUSTMENT = "manual_adjustment"
    FEE = "fee"
    REFUND = "refund"


class TransactionStatus(str, enum.Enum):
    """Status of a transaction."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


class Transaction(BaseModel):
    """
    Transaction model for tracking all financial movements.
    
    Attributes:
        user_id: Reference to the user
        bucket_id: Optional reference to a bucket (for bucket transactions)
        amount: Transaction amount (positive for credits, negative for debits)
        type: Type of transaction
        status: Current status
        description: Human-readable description
        reference_id: External reference (e.g., payment gateway ID)
        metadata: JSON string for additional transaction data
    """
    
    __tablename__ = "transactions"
    
    # Foreign keys
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the user"
    )
    bucket_id = Column(
        Integer,
        ForeignKey("buckets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Optional reference to a bucket"
    )
    source_bucket_id = Column(
        Integer,
        ForeignKey("buckets.id", ondelete="SET NULL"),
        nullable=True,
        doc="Source bucket for transfers"
    )
    destination_bucket_id = Column(
        Integer,
        ForeignKey("buckets.id", ondelete="SET NULL"),
        nullable=True,
        doc="Destination bucket for transfers"
    )
    
    # Transaction details
    amount = Column(
        Numeric(12, 2),
        nullable=False,
        doc="Transaction amount (positive for credits, negative for debits)"
    )
    fee_amount = Column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
        doc="Fee charged for this transaction"
    )
    
    # Type and status
    type = Column(
        Enum(TransactionType),
        nullable=False,
        index=True,
        doc="Type of transaction"
    )
    status = Column(
        Enum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True,
        doc="Current status of the transaction"
    )
    
    # Description and reference
    description = Column(
        Text,
        nullable=True,
        doc="Human-readable description of the transaction"
    )
    reference_id = Column(
        String(100),
        nullable=True,
        index=True,
        doc="External reference ID (e.g., payment gateway)"
    )
    
    # Metadata for additional info
    metadata_json = Column(
        Text,
        nullable=True,
        doc="JSON string for additional transaction data"
    )
    
    # For AI-related transactions
    ai_recommendation_id = Column(
        String(100),
        nullable=True,
        doc="Reference to AI recommendation that triggered this transaction"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions"
    )
    bucket: Mapped[Optional["Bucket"]] = relationship(
        "Bucket",
        back_populates="transactions",
        foreign_keys=[bucket_id]
    )
    source_bucket: Mapped[Optional["Bucket"]] = relationship(
        "Bucket",
        foreign_keys=[source_bucket_id]
    )
    destination_bucket: Mapped[Optional["Bucket"]] = relationship(
        "Bucket",
        foreign_keys=[destination_bucket_id]
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_transactions_user_type", "user_id", "type"),
        Index("ix_transactions_user_status", "user_id", "status"),
        Index("ix_transactions_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount})>"
    
    @property
    def net_amount(self) -> Decimal:
        """Calculate net amount after fees."""
        return self.amount - self.fee_amount
    
    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.amount > 0
    
    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.amount < 0

