"""
Bucket (Money Jar) related Pydantic schemas.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.models.bucket import BucketCategory, BucketStatus


class BucketBase(BaseModel):
    """Base schema for bucket data."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Bucket name")
    description: Optional[str] = Field(None, max_length=500, description="Bucket description")
    target_amount: Decimal = Field(..., gt=0, decimal_places=2, description="Target amount to save")
    category: BucketCategory = Field(default=BucketCategory.SAVINGS, description="Bucket category")
    priority: int = Field(default=5, ge=1, le=10, description="Priority (1=highest, 10=lowest)")
    deadline: Optional[date] = Field(None, description="Target date to reach the goal")
    icon: str = Field(default="piggy-bank", max_length=50, description="Icon identifier")
    color: str = Field(default="#4CAF50", max_length=7, description="Hex color code")
    auto_allocate: bool = Field(default=True, description="Enable AI auto-allocation")


class BucketCreate(BucketBase):
    """Schema for creating a new bucket."""
    
    initial_amount: Optional[Decimal] = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
        description="Initial amount to deposit"
    )
    allocation_percent: Optional[Decimal] = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        decimal_places=2,
        description="Percentage of income to allocate"
    )
    
    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v: Optional[date]) -> Optional[date]:
        """Ensure deadline is in the future."""
        if v and v < date.today():
            raise ValueError("Deadline must be in the future")
        return v


class BucketUpdate(BaseModel):
    """Schema for updating a bucket."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    target_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category: Optional[BucketCategory] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    deadline: Optional[date] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    auto_allocate: Optional[bool] = None
    allocation_percent: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    status: Optional[BucketStatus] = None


class BucketResponse(BaseModel):
    """Schema for bucket response."""
    
    id: int
    user_id: int
    name: str
    description: Optional[str]
    target_amount: Decimal
    current_amount: Decimal
    category: BucketCategory
    priority: int
    deadline: Optional[date]
    icon: str
    color: str
    auto_allocate: bool
    allocation_percent: Decimal
    status: BucketStatus
    progress_percent: float
    remaining_amount: Decimal
    is_goal_reached: bool
    days_until_deadline: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BucketDeposit(BaseModel):
    """Schema for depositing to a bucket."""
    
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Amount to deposit")
    description: Optional[str] = Field(None, max_length=255, description="Transaction description")


class BucketWithdraw(BaseModel):
    """Schema for withdrawing from a bucket."""
    
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Amount to withdraw")
    description: Optional[str] = Field(None, max_length=255, description="Transaction description")


class BucketTransfer(BaseModel):
    """Schema for transferring between buckets."""
    
    source_bucket_id: int = Field(..., description="Source bucket ID")
    destination_bucket_id: int = Field(..., description="Destination bucket ID")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Amount to transfer")
    description: Optional[str] = Field(None, max_length=255, description="Transfer description")
    
    @field_validator("destination_bucket_id")
    @classmethod
    def validate_different_buckets(cls, v: int, info) -> int:
        """Ensure source and destination are different."""
        if "source_bucket_id" in info.data and v == info.data["source_bucket_id"]:
            raise ValueError("Source and destination buckets must be different")
        return v


class BucketSummary(BaseModel):
    """Schema for bucket summary/statistics."""
    
    total_buckets: int
    active_buckets: int
    total_target: Decimal
    total_saved: Decimal
    overall_progress: float
    buckets_by_category: dict[str, int]
    upcoming_deadlines: List["BucketResponse"] = []
    
    class Config:
        from_attributes = True


class BucketListResponse(BaseModel):
    """Schema for paginated bucket list response."""
    
    items: List[BucketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

