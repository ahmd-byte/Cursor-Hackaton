"""
Pydantic schemas module.

Contains all request/response schemas for API validation.
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenPayload,
)
from app.schemas.bucket import (
    BucketCreate,
    BucketUpdate,
    BucketResponse,
    BucketDeposit,
    BucketTransfer,
    BucketSummary,
)
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionType,
    TransactionStatus,
)
from app.schemas.ai_allocation import (
    AllocationRequest,
    AllocationResponse,
    AllocationRecommendation,
    FinancialInsight,
    SpendingAnalysis,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenPayload",
    # Bucket schemas
    "BucketCreate",
    "BucketUpdate",
    "BucketResponse",
    "BucketDeposit",
    "BucketTransfer",
    "BucketSummary",
    # Transaction schemas
    "TransactionCreate",
    "TransactionResponse",
    "TransactionType",
    "TransactionStatus",
    # AI allocation schemas
    "AllocationRequest",
    "AllocationResponse",
    "AllocationRecommendation",
    "FinancialInsight",
    "SpendingAnalysis",
]

