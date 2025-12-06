"""
Money Jars (Buckets) API endpoints.

Provides CRUD operations and fund management for financial goal buckets.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.models.user import User
from app.models.bucket import BucketCategory, BucketStatus
from app.schemas.bucket import (
    BucketCreate,
    BucketUpdate,
    BucketResponse,
    BucketDeposit,
    BucketWithdraw,
    BucketTransfer,
    BucketSummary,
    BucketListResponse,
)
from app.services.bucket_service import BucketService
from app.utils.security import get_current_user

router = APIRouter()


@router.post(
    "",
    response_model=BucketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bucket",
    description="Create a new money jar/bucket for a financial goal."
)
async def create_bucket(
    bucket_data: BucketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> BucketResponse:
    """
    Create a new money jar (bucket) for tracking a financial goal.
    
    - **name**: Display name for the bucket
    - **target_amount**: Goal amount to save
    - **category**: Category of the financial goal
    - **priority**: Priority level (1=highest, 10=lowest)
    - **deadline**: Optional target date
    - **auto_allocate**: Enable AI auto-allocation
    """
    service = BucketService(db)
    bucket = await service.create_bucket(current_user.id, bucket_data)
    return BucketResponse.model_validate(bucket)


@router.get(
    "",
    response_model=BucketListResponse,
    summary="List all buckets",
    description="Get all buckets for the current user with optional filtering."
)
async def list_buckets(
    status: Optional[BucketStatus] = Query(None, description="Filter by status"),
    category: Optional[BucketCategory] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> BucketListResponse:
    """
    List all money jars for the current user.
    
    Supports filtering by status and category, with pagination.
    Results are ordered by priority (ascending) and creation date (descending).
    """
    service = BucketService(db)
    buckets, total = await service.get_user_buckets(
        current_user.id,
        status=status,
        category=category,
        page=page,
        page_size=page_size
    )
    
    return BucketListResponse(
        items=[BucketResponse.model_validate(b) for b in buckets],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get(
    "/summary",
    response_model=BucketSummary,
    summary="Get bucket summary",
    description="Get aggregated statistics for all user's buckets."
)
async def get_bucket_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> BucketSummary:
    """
    Get summary statistics for all money jars.
    
    Returns:
    - Total and active bucket counts
    - Total target and saved amounts
    - Overall progress percentage
    - Breakdown by category
    - Upcoming deadline alerts
    """
    service = BucketService(db)
    return await service.get_bucket_summary(current_user.id)


@router.get(
    "/{bucket_id}",
    response_model=BucketResponse,
    summary="Get bucket details",
    description="Get details of a specific bucket."
)
async def get_bucket(
    bucket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> BucketResponse:
    """
    Get detailed information about a specific money jar.
    
    Includes progress percentage, remaining amount, and days until deadline.
    """
    service = BucketService(db)
    bucket = await service.get_bucket(bucket_id, current_user.id)
    
    if not bucket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bucket not found"
        )
    
    return BucketResponse.model_validate(bucket)


@router.put(
    "/{bucket_id}",
    response_model=BucketResponse,
    summary="Update bucket",
    description="Update a bucket's properties."
)
async def update_bucket(
    bucket_id: int,
    bucket_data: BucketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> BucketResponse:
    """
    Update a money jar's properties.
    
    All fields are optional. Only provided fields will be updated.
    """
    service = BucketService(db)
    bucket = await service.update_bucket(bucket_id, current_user.id, bucket_data)
    
    if not bucket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bucket not found"
        )
    
    return BucketResponse.model_validate(bucket)


@router.delete(
    "/{bucket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete bucket",
    description="Delete a bucket and its transaction history."
)
async def delete_bucket(
    bucket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Delete a money jar.
    
    Warning: This will also delete all associated transaction records.
    """
    service = BucketService(db)
    deleted = await service.delete_bucket(bucket_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bucket not found"
        )


@router.post(
    "/{bucket_id}/deposit",
    response_model=BucketResponse,
    summary="Deposit to bucket",
    description="Add funds to a bucket."
)
async def deposit_to_bucket(
    bucket_id: int,
    deposit_data: BucketDeposit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> BucketResponse:
    """
    Deposit funds to a money jar.
    
    - **amount**: Amount to deposit (must be positive)
    - **description**: Optional description for the transaction
    
    If the deposit causes the bucket to reach its target,
    the status will automatically change to 'completed'.
    """
    service = BucketService(db)
    bucket = await service.deposit_to_bucket(
        bucket_id,
        current_user.id,
        deposit_data.amount,
        deposit_data.description
    )
    
    if not bucket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bucket not found"
        )
    
    return BucketResponse.model_validate(bucket)


@router.post(
    "/{bucket_id}/withdraw",
    response_model=BucketResponse,
    summary="Withdraw from bucket",
    description="Withdraw funds from a bucket."
)
async def withdraw_from_bucket(
    bucket_id: int,
    withdraw_data: BucketWithdraw,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> BucketResponse:
    """
    Withdraw funds from a money jar.
    
    - **amount**: Amount to withdraw (must not exceed current balance)
    - **description**: Optional description for the transaction
    """
    service = BucketService(db)
    
    try:
        bucket = await service.withdraw_from_bucket(
            bucket_id,
            current_user.id,
            withdraw_data.amount,
            withdraw_data.description
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not bucket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bucket not found"
        )
    
    return BucketResponse.model_validate(bucket)


@router.post(
    "/transfer",
    response_model=dict,
    summary="Transfer between buckets",
    description="Transfer funds from one bucket to another."
)
async def transfer_between_buckets(
    transfer_data: BucketTransfer,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Transfer funds between two money jars.
    
    - **source_bucket_id**: ID of the source bucket
    - **destination_bucket_id**: ID of the destination bucket
    - **amount**: Amount to transfer
    - **description**: Optional description
    """
    service = BucketService(db)
    
    try:
        source, destination = await service.transfer_between_buckets(
            transfer_data.source_bucket_id,
            transfer_data.destination_bucket_id,
            current_user.id,
            transfer_data.amount,
            transfer_data.description
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return {
        "message": "Transfer successful",
        "source_bucket": BucketResponse.model_validate(source),
        "destination_bucket": BucketResponse.model_validate(destination)
    }

