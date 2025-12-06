"""
Bucket (Money Jar) model for financial goal management.
"""

from decimal import Decimal
from datetime import date
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Numeric,
    Integer,
    Date,
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
    from app.models.transaction import Transaction


class BucketCategory(str, enum.Enum):
    """Categories for money jar buckets."""
    
    EMERGENCY = "emergency"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    VACATION = "vacation"
    EDUCATION = "education"
    HOUSING = "housing"
    TRANSPORTATION = "transportation"
    HEALTHCARE = "healthcare"
    RETIREMENT = "retirement"
    DEBT_REPAYMENT = "debt_repayment"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    CHARITY = "charity"
    OTHER = "other"


class BucketStatus(str, enum.Enum):
    """Status of a bucket."""
    
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Bucket(BaseModel):
    """
    Money jar (bucket) model for financial goal management.
    
    Attributes:
        user_id: Reference to the owning user
        name: Display name for the bucket
        description: Optional description of the goal
        target_amount: Goal amount to save
        current_amount: Current balance in the bucket
        category: Category of the financial goal
        priority: Priority level (1 = highest)
        deadline: Optional target date to reach the goal
        auto_allocate: Whether AI should auto-allocate to this bucket
        allocation_percent: Suggested percentage of income to allocate
        status: Current status of the bucket
    """
    
    __tablename__ = "buckets"
    
    # Foreign key to user
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the owning user"
    )
    
    # Bucket details
    name = Column(
        String(100),
        nullable=False,
        doc="Display name for the bucket"
    )
    description = Column(
        Text,
        nullable=True,
        doc="Optional description of the financial goal"
    )
    icon = Column(
        String(50),
        default="piggy-bank",
        nullable=False,
        doc="Icon identifier for UI display"
    )
    color = Column(
        String(7),
        default="#4CAF50",
        nullable=False,
        doc="Hex color code for UI display"
    )
    
    # Financial tracking
    target_amount = Column(
        Numeric(12, 2),
        nullable=False,
        doc="Goal amount to save"
    )
    current_amount = Column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
        doc="Current balance in the bucket"
    )
    
    # Categorization
    category = Column(
        Enum(BucketCategory),
        default=BucketCategory.SAVINGS,
        nullable=False,
        doc="Category of the financial goal"
    )
    
    # Priority and timing
    priority = Column(
        Integer,
        default=5,
        nullable=False,
        doc="Priority level from 1 (highest) to 10 (lowest)"
    )
    deadline = Column(
        Date,
        nullable=True,
        doc="Optional target date to reach the goal"
    )
    
    # AI allocation settings
    auto_allocate = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether AI should auto-allocate funds to this bucket"
    )
    allocation_percent = Column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        doc="Suggested percentage of income to allocate"
    )
    
    # Status
    status = Column(
        Enum(BucketStatus),
        default=BucketStatus.ACTIVE,
        nullable=False,
        doc="Current status of the bucket"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="buckets"
    )
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="bucket",
        lazy="selectin"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_buckets_user_status", "user_id", "status"),
        Index("ix_buckets_user_category", "user_id", "category"),
    )
    
    def __repr__(self) -> str:
        return f"<Bucket(id={self.id}, name={self.name}, user_id={self.user_id})>"
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress towards the target as a percentage."""
        if self.target_amount == 0:
            return 100.0
        return float((self.current_amount / self.target_amount) * 100)
    
    @property
    def remaining_amount(self) -> Decimal:
        """Calculate remaining amount to reach the target."""
        remaining = self.target_amount - self.current_amount
        return max(Decimal("0.00"), remaining)
    
    @property
    def is_goal_reached(self) -> bool:
        """Check if the goal has been reached."""
        return self.current_amount >= self.target_amount
    
    @property
    def days_until_deadline(self) -> Optional[int]:
        """Calculate days remaining until deadline."""
        if not self.deadline:
            return None
        today = date.today()
        delta = self.deadline - today
        return delta.days

