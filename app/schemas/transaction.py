"""
Transaction-related Pydantic schemas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.transaction import TransactionType, TransactionStatus


class TransactionBase(BaseModel):
    """Base schema for transaction data."""
    
    amount: Decimal = Field(..., decimal_places=2, description="Transaction amount")
    type: TransactionType = Field(..., description="Transaction type")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""
    
    bucket_id: Optional[int] = Field(None, description="Associated bucket ID")
    source_bucket_id: Optional[int] = Field(None, description="Source bucket for transfers")
    destination_bucket_id: Optional[int] = Field(None, description="Destination bucket for transfers")
    reference_id: Optional[str] = Field(None, max_length=100, description="External reference ID")
    metadata_json: Optional[str] = Field(None, description="Additional metadata as JSON")


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    
    id: int
    user_id: int
    bucket_id: Optional[int]
    source_bucket_id: Optional[int]
    destination_bucket_id: Optional[int]
    amount: Decimal
    fee_amount: Decimal
    type: TransactionType
    status: TransactionStatus
    description: Optional[str]
    reference_id: Optional[str]
    net_amount: Decimal
    is_credit: bool
    is_debit: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list."""
    
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TransactionSummary(BaseModel):
    """Schema for transaction summary/statistics."""
    
    total_transactions: int
    total_credits: Decimal
    total_debits: Decimal
    net_change: Decimal
    transactions_by_type: dict[str, int]
    transactions_by_status: dict[str, int]
    recent_transactions: List[TransactionResponse] = []


class WageAdvanceRequest(BaseModel):
    """Schema for requesting early wage access."""
    
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Amount to advance")
    description: Optional[str] = Field(None, max_length=255, description="Reason for advance")
    
    
class WageAdvanceResponse(BaseModel):
    """Schema for wage advance response."""
    
    transaction_id: int
    amount: Decimal
    fee_amount: Decimal
    net_amount: Decimal
    status: TransactionStatus
    available_balance_after: Decimal
    message: str


class PayrollWebhookPayload(BaseModel):
    """Schema for payroll webhook from employer."""
    
    employer_id: str = Field(..., description="Employer identifier")
    employee_id: str = Field(..., description="Employee identifier")
    pay_period_start: datetime = Field(..., description="Pay period start date")
    pay_period_end: datetime = Field(..., description="Pay period end date")
    gross_amount: Decimal = Field(..., decimal_places=2, description="Gross pay amount")
    net_amount: Decimal = Field(..., decimal_places=2, description="Net pay amount")
    days_worked: int = Field(..., ge=0, description="Number of days worked")
    deductions: Optional[dict] = Field(None, description="Deductions breakdown")
    reference_id: str = Field(..., description="Payroll reference ID")


class WageAvailableResponse(BaseModel):
    """Schema for available wage balance response."""
    
    user_id: int
    daily_rate: Decimal
    days_worked_this_period: int
    earned_wages: Decimal
    available_for_advance: Decimal
    max_advance_percent: float
    pending_advances: Decimal
    next_pay_date: datetime

