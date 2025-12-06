"""
Tests for bucket service.
"""

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.bucket_service import BucketService
from app.models.user import User
from app.models.bucket import BucketCategory
from app.schemas.bucket import BucketCreate, BucketUpdate


@pytest.mark.asyncio
async def test_create_bucket(test_db: AsyncSession):
    """Test bucket creation via service."""
    # Create test user first
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create bucket
    service = BucketService(test_db)
    bucket_data = BucketCreate(
        name="Test Bucket",
        target_amount=Decimal("5000.00"),
        category=BucketCategory.SAVINGS,
        priority=1
    )
    
    bucket = await service.create_bucket(user.id, bucket_data)
    
    assert bucket.name == "Test Bucket"
    assert bucket.target_amount == Decimal("5000.00")
    assert bucket.user_id == user.id


@pytest.mark.asyncio
async def test_deposit_to_bucket(test_db: AsyncSession):
    """Test depositing to bucket via service."""
    # Create user and bucket
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    service = BucketService(test_db)
    bucket_data = BucketCreate(
        name="Test Bucket",
        target_amount=Decimal("1000.00"),
        category=BucketCategory.SAVINGS
    )
    bucket = await service.create_bucket(user.id, bucket_data)
    
    # Deposit
    updated = await service.deposit_to_bucket(
        bucket.id,
        user.id,
        Decimal("250.00"),
        "Test deposit"
    )
    
    assert updated.current_amount == Decimal("250.00")
    assert updated.progress_percent == 25.0


@pytest.mark.asyncio
async def test_transfer_between_buckets(test_db: AsyncSession):
    """Test transferring between buckets."""
    # Create user and two buckets
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    service = BucketService(test_db)
    
    bucket1_data = BucketCreate(
        name="Source Bucket",
        target_amount=Decimal("1000.00"),
        initial_amount=Decimal("500.00"),
        category=BucketCategory.SAVINGS
    )
    bucket1 = await service.create_bucket(user.id, bucket1_data)
    
    bucket2_data = BucketCreate(
        name="Destination Bucket",
        target_amount=Decimal("1000.00"),
        category=BucketCategory.SAVINGS
    )
    bucket2 = await service.create_bucket(user.id, bucket2_data)
    
    # Transfer
    source, dest = await service.transfer_between_buckets(
        bucket1.id,
        bucket2.id,
        user.id,
        Decimal("200.00")
    )
    
    assert source.current_amount == Decimal("300.00")
    assert dest.current_amount == Decimal("200.00")

