"""
Bucket (Money Jar) service for managing financial goal buckets.

Provides business logic for creating, updating, and managing money jars.
"""

from decimal import Decimal
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.bucket import Bucket, BucketCategory, BucketStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.user import User
from app.schemas.bucket import (
    BucketCreate,
    BucketUpdate,
    BucketSummary,
)


class BucketService:
    """
    Service class for bucket (money jar) operations.
    
    Handles all business logic related to creating, updating,
    and managing financial goal buckets.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
    
    async def create_bucket(
        self,
        user_id: int,
        bucket_data: BucketCreate
    ) -> Bucket:
        """
        Create a new bucket for a user.
        
        Args:
            user_id: ID of the user creating the bucket
            bucket_data: Bucket creation data
            
        Returns:
            Created Bucket object
        """
        bucket = Bucket(
            user_id=user_id,
            name=bucket_data.name,
            description=bucket_data.description,
            target_amount=bucket_data.target_amount,
            current_amount=bucket_data.initial_amount or Decimal("0.00"),
            category=bucket_data.category,
            priority=bucket_data.priority,
            deadline=bucket_data.deadline,
            icon=bucket_data.icon,
            color=bucket_data.color,
            auto_allocate=bucket_data.auto_allocate,
            allocation_percent=bucket_data.allocation_percent or Decimal("0.00"),
        )
        
        self.db.add(bucket)
        await self.db.commit()
        await self.db.refresh(bucket)
        
        # If initial amount is provided, create a transaction
        if bucket_data.initial_amount and bucket_data.initial_amount > 0:
            await self._create_bucket_transaction(
                user_id=user_id,
                bucket_id=bucket.id,
                amount=bucket_data.initial_amount,
                transaction_type=TransactionType.BUCKET_DEPOSIT,
                description="Initial deposit"
            )
        
        return bucket
    
    async def get_bucket(
        self,
        bucket_id: int,
        user_id: int
    ) -> Optional[Bucket]:
        """
        Get a bucket by ID for a specific user.
        
        Args:
            bucket_id: ID of the bucket
            user_id: ID of the user (for ownership verification)
            
        Returns:
            Bucket object or None if not found
        """
        result = await self.db.execute(
            select(Bucket).where(
                and_(Bucket.id == bucket_id, Bucket.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_buckets(
        self,
        user_id: int,
        status: Optional[BucketStatus] = None,
        category: Optional[BucketCategory] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Bucket], int]:
        """
        Get all buckets for a user with optional filtering.
        
        Args:
            user_id: ID of the user
            status: Optional status filter
            category: Optional category filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (list of buckets, total count)
        """
        # Build query
        query = select(Bucket).where(Bucket.user_id == user_id)
        
        if status:
            query = query.where(Bucket.status == status)
        if category:
            query = query.where(Bucket.category == category)
        
        # Get total count
        count_query = select(func.count(Bucket.id)).where(Bucket.user_id == user_id)
        if status:
            count_query = count_query.where(Bucket.status == status)
        if category:
            count_query = count_query.where(Bucket.category == category)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Bucket.priority.asc(), Bucket.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        buckets = result.scalars().all()
        
        return list(buckets), total
    
    async def update_bucket(
        self,
        bucket_id: int,
        user_id: int,
        bucket_data: BucketUpdate
    ) -> Optional[Bucket]:
        """
        Update a bucket.
        
        Args:
            bucket_id: ID of the bucket to update
            user_id: ID of the user (for ownership verification)
            bucket_data: Update data
            
        Returns:
            Updated Bucket object or None if not found
        """
        bucket = await self.get_bucket(bucket_id, user_id)
        if not bucket:
            return None
        
        # Update only provided fields
        update_data = bucket_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bucket, field, value)
        
        await self.db.commit()
        await self.db.refresh(bucket)
        
        return bucket
    
    async def delete_bucket(
        self,
        bucket_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a bucket.
        
        Args:
            bucket_id: ID of the bucket to delete
            user_id: ID of the user (for ownership verification)
            
        Returns:
            True if deleted, False if not found
        """
        bucket = await self.get_bucket(bucket_id, user_id)
        if not bucket:
            return False
        
        await self.db.delete(bucket)
        await self.db.commit()
        
        return True
    
    async def deposit_to_bucket(
        self,
        bucket_id: int,
        user_id: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Optional[Bucket]:
        """
        Deposit funds to a bucket.
        
        Args:
            bucket_id: ID of the bucket
            user_id: ID of the user
            amount: Amount to deposit (must be positive)
            description: Optional transaction description
            
        Returns:
            Updated Bucket object or None if not found
        """
        bucket = await self.get_bucket(bucket_id, user_id)
        if not bucket:
            return None
        
        # Update bucket balance
        bucket.current_amount += amount
        
        # Check if goal is reached
        if bucket.current_amount >= bucket.target_amount:
            bucket.status = BucketStatus.COMPLETED
        
        # Create transaction record
        await self._create_bucket_transaction(
            user_id=user_id,
            bucket_id=bucket_id,
            amount=amount,
            transaction_type=TransactionType.BUCKET_DEPOSIT,
            description=description or f"Deposit to {bucket.name}"
        )
        
        await self.db.commit()
        await self.db.refresh(bucket)
        
        return bucket
    
    async def withdraw_from_bucket(
        self,
        bucket_id: int,
        user_id: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Optional[Bucket]:
        """
        Withdraw funds from a bucket.
        
        Args:
            bucket_id: ID of the bucket
            user_id: ID of the user
            amount: Amount to withdraw (must be positive and <= balance)
            description: Optional transaction description
            
        Returns:
            Updated Bucket object or None if not found/insufficient funds
            
        Raises:
            ValueError: If insufficient funds
        """
        bucket = await self.get_bucket(bucket_id, user_id)
        if not bucket:
            return None
        
        if amount > bucket.current_amount:
            raise ValueError("Insufficient funds in bucket")
        
        # Update bucket balance
        bucket.current_amount -= amount
        
        # Update status if was completed
        if bucket.status == BucketStatus.COMPLETED and bucket.current_amount < bucket.target_amount:
            bucket.status = BucketStatus.ACTIVE
        
        # Create transaction record
        await self._create_bucket_transaction(
            user_id=user_id,
            bucket_id=bucket_id,
            amount=-amount,  # Negative for withdrawal
            transaction_type=TransactionType.BUCKET_WITHDRAWAL,
            description=description or f"Withdrawal from {bucket.name}"
        )
        
        await self.db.commit()
        await self.db.refresh(bucket)
        
        return bucket
    
    async def transfer_between_buckets(
        self,
        source_bucket_id: int,
        destination_bucket_id: int,
        user_id: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> tuple[Optional[Bucket], Optional[Bucket]]:
        """
        Transfer funds between two buckets.
        
        Args:
            source_bucket_id: ID of the source bucket
            destination_bucket_id: ID of the destination bucket
            user_id: ID of the user
            amount: Amount to transfer
            description: Optional transaction description
            
        Returns:
            Tuple of (source bucket, destination bucket) or (None, None) if error
            
        Raises:
            ValueError: If insufficient funds or invalid buckets
        """
        if source_bucket_id == destination_bucket_id:
            raise ValueError("Cannot transfer to the same bucket")
        
        source = await self.get_bucket(source_bucket_id, user_id)
        destination = await self.get_bucket(destination_bucket_id, user_id)
        
        if not source or not destination:
            raise ValueError("One or both buckets not found")
        
        if amount > source.current_amount:
            raise ValueError("Insufficient funds in source bucket")
        
        # Perform transfer
        source.current_amount -= amount
        destination.current_amount += amount
        
        # Update statuses
        if source.status == BucketStatus.COMPLETED and source.current_amount < source.target_amount:
            source.status = BucketStatus.ACTIVE
        if destination.current_amount >= destination.target_amount:
            destination.status = BucketStatus.COMPLETED
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=TransactionType.BUCKET_TRANSFER,
            status=TransactionStatus.COMPLETED,
            source_bucket_id=source_bucket_id,
            destination_bucket_id=destination_bucket_id,
            description=description or f"Transfer from {source.name} to {destination.name}"
        )
        self.db.add(transaction)
        
        await self.db.commit()
        await self.db.refresh(source)
        await self.db.refresh(destination)
        
        return source, destination
    
    async def get_bucket_summary(self, user_id: int) -> BucketSummary:
        """
        Get summary statistics for user's buckets.
        
        Args:
            user_id: ID of the user
            
        Returns:
            BucketSummary with aggregated statistics
        """
        # Get all buckets
        result = await self.db.execute(
            select(Bucket).where(Bucket.user_id == user_id)
        )
        buckets = result.scalars().all()
        
        # Calculate statistics
        total_buckets = len(buckets)
        active_buckets = len([b for b in buckets if b.status == BucketStatus.ACTIVE])
        total_target = sum(b.target_amount for b in buckets)
        total_saved = sum(b.current_amount for b in buckets)
        
        overall_progress = 0.0
        if total_target > 0:
            overall_progress = float((total_saved / total_target) * 100)
        
        # Count by category
        buckets_by_category = {}
        for bucket in buckets:
            cat = bucket.category.value
            buckets_by_category[cat] = buckets_by_category.get(cat, 0) + 1
        
        # Get upcoming deadlines (next 30 days)
        today = date.today()
        thirty_days = today + timedelta(days=30)
        upcoming = [
            b for b in buckets
            if b.deadline and today <= b.deadline <= thirty_days and b.status == BucketStatus.ACTIVE
        ]
        upcoming.sort(key=lambda x: x.deadline)
        
        return BucketSummary(
            total_buckets=total_buckets,
            active_buckets=active_buckets,
            total_target=total_target,
            total_saved=total_saved,
            overall_progress=overall_progress,
            buckets_by_category=buckets_by_category,
            upcoming_deadlines=upcoming[:5]  # Top 5 upcoming
        )
    
    async def _create_bucket_transaction(
        self,
        user_id: int,
        bucket_id: int,
        amount: Decimal,
        transaction_type: TransactionType,
        description: str
    ) -> Transaction:
        """Create a transaction record for bucket operations."""
        transaction = Transaction(
            user_id=user_id,
            bucket_id=bucket_id,
            amount=amount,
            type=transaction_type,
            status=TransactionStatus.COMPLETED,
            description=description
        )
        self.db.add(transaction)
        return transaction
    
    async def get_auto_allocate_buckets(self, user_id: int) -> List[Bucket]:
        """
        Get all active buckets with auto-allocation enabled.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of buckets eligible for auto-allocation
        """
        result = await self.db.execute(
            select(Bucket).where(
                and_(
                    Bucket.user_id == user_id,
                    Bucket.status == BucketStatus.ACTIVE,
                    Bucket.auto_allocate == True
                )
            ).order_by(Bucket.priority.asc())
        )
        return list(result.scalars().all())

