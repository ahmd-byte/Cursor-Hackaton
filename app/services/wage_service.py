"""
Wage service for early wage access functionality.

Provides business logic for wage calculations, advances, and payroll integration.
"""

from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.config import settings


class WageService:
    """
    Service class for wage-related operations.
    
    Handles early wage access calculations, advance requests,
    and payroll webhook processing.
    
    Tiered Daily Pay Formula:
    - Daily Income (Y) = Monthly Salary (X) / 30
    - Savings Amount (Z) = Y * tier_percentage
    - Max Daily Pay = Y - Z
    
    Tier percentages:
    - Month 1: 20%
    - Month 2: 15%
    - Month 3+: 5%
    """
    
    # Tiered savings percentages
    TIER_PERCENTAGES = {
        1: Decimal("0.20"),  # First month: 20%
        2: Decimal("0.15"),  # Second month: 15%
        3: Decimal("0.05"),  # Third month onwards: 5%
    }
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
    
    def get_tier_percentage(self, user: User) -> Decimal:
        """
        Get the savings tier percentage based on user's tenure.
        
        Args:
            user: User object
            
        Returns:
            Decimal percentage (0.20, 0.15, or 0.05)
        """
        tier = user.current_savings_tier or 1
        
        # Cap at tier 3 (5%)
        if tier >= 3:
            return self.TIER_PERCENTAGES[3]
        
        return self.TIER_PERCENTAGES.get(tier, self.TIER_PERCENTAGES[3])
    
    def calculate_daily_amounts(self, user: User) -> Dict[str, Any]:
        """
        Calculate daily income and savings allocation.
        
        Formula:
        - Y (daily income) = X (monthly salary) / 30
        - Z (savings amount) = Y * tier_percentage
        - Max daily pay = Y - Z
        
        Args:
            user: User object
            
        Returns:
            Dictionary with daily calculations
        """
        monthly_salary = user.monthly_salary or Decimal("0.00")
        
        # Y = X / 30 (daily income)
        daily_income = monthly_salary / Decimal("30")
        
        # Get tier percentage based on user tenure
        tier_percentage = self.get_tier_percentage(user)
        tier_number = min(user.current_savings_tier or 1, 3)
        
        # Z = Y * tier_percentage (savings allocation for buckets)
        savings_allocation = daily_income * tier_percentage
        
        # Max daily pay = Y - Z
        max_daily_pay = daily_income - savings_allocation
        
        return {
            "monthly_salary": monthly_salary,
            "daily_income": daily_income,
            "tier_number": tier_number,
            "tier_percentage": float(tier_percentage * 100),  # As percentage
            "savings_allocation": savings_allocation,  # Z - goes to buckets
            "max_daily_pay": max_daily_pay,
            "formula": {
                "Y": f"{monthly_salary} / 30 = {daily_income:.2f}",
                "Z": f"{daily_income:.2f} * {tier_percentage} = {savings_allocation:.2f}",
                "max_pay": f"{daily_income:.2f} - {savings_allocation:.2f} = {max_daily_pay:.2f}"
            }
        }
    
    async def get_available_wage_balance(self, user: User) -> Dict[str, Any]:
        """
        Calculate the available wage balance for early access.
        
        Uses tiered daily pay formula:
        - Y = monthly_salary / 30 (daily income)
        - Z = Y * tier_percentage (savings for buckets)
        - max_daily_pay = Y - Z
        
        Args:
            user: User object
            
        Returns:
            Dictionary with wage availability details
        """
        today = datetime.now()
        
        # Calculate days worked in current pay period
        pay_cycle_day = user.pay_cycle_day or 25
        
        # Determine pay period start
        if today.day >= pay_cycle_day:
            period_start = today.replace(day=pay_cycle_day)
        else:
            # Previous month
            if today.month == 1:
                period_start = today.replace(year=today.year - 1, month=12, day=pay_cycle_day)
            else:
                period_start = today.replace(month=today.month - 1, day=pay_cycle_day)
        
        # Calculate days worked (excluding weekends for simplicity)
        days_worked = self._calculate_working_days(period_start.date(), today.date())
        
        # Calculate tiered daily amounts
        daily_calc = self.calculate_daily_amounts(user)
        max_daily_pay = daily_calc["max_daily_pay"]
        savings_allocation = daily_calc["savings_allocation"]
        
        # Total earned = max_daily_pay * days_worked
        earned_wages = max_daily_pay * days_worked
        
        # Total savings to allocate to buckets
        total_savings_for_buckets = savings_allocation * days_worked
        
        # Get pending advances
        pending_advances = await self._get_pending_advances(user.id)
        
        # Available for advance (what user can cash out)
        available_for_advance = max(Decimal("0.00"), earned_wages - pending_advances)
        
        # Calculate next pay date
        if today.day >= pay_cycle_day:
            if today.month == 12:
                next_pay = today.replace(year=today.year + 1, month=1, day=pay_cycle_day)
            else:
                next_pay = today.replace(month=today.month + 1, day=pay_cycle_day)
        else:
            next_pay = today.replace(day=pay_cycle_day)
        
        return {
            "user_id": user.id,
            # Tiered calculation details
            "monthly_salary": daily_calc["monthly_salary"],
            "daily_income": daily_calc["daily_income"],
            "tier_number": daily_calc["tier_number"],
            "tier_percentage": daily_calc["tier_percentage"],
            "max_daily_pay": max_daily_pay,
            "daily_savings_allocation": savings_allocation,
            # Period totals
            "days_worked_this_period": days_worked,
            "earned_wages": earned_wages,  # What can be cashed out
            "total_savings_for_buckets": total_savings_for_buckets,  # Z * days - for AI to allocate
            # Availability
            "available_for_advance": available_for_advance,
            "pending_advances": pending_advances,
            "next_pay_date": next_pay,
            # Formula breakdown
            "formula": daily_calc["formula"]
        }
    
    async def request_wage_advance(
        self,
        user: User,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a wage advance request.
        
        Args:
            user: User requesting the advance
            amount: Amount to advance
            description: Optional description
            
        Returns:
            Dictionary with advance details
            
        Raises:
            ValueError: If amount exceeds available balance
        """
        # Get available balance
        balance_info = await self.get_available_wage_balance(user)
        available = balance_info["available_for_advance"]
        
        if amount > available:
            raise ValueError(
                f"Requested amount ({amount}) exceeds available balance ({available})"
            )
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Calculate fee
        fee_percent = Decimal(str(settings.advance_fee_percent)) / Decimal("100")
        fee_amount = amount * fee_percent
        net_amount = amount - fee_amount
        
        # Create advance transaction
        advance_transaction = Transaction(
            user_id=user.id,
            amount=amount,
            fee_amount=fee_amount,
            type=TransactionType.WAGE_ADVANCE,
            status=TransactionStatus.COMPLETED,
            description=description or "Early wage access"
        )
        self.db.add(advance_transaction)
        
        # Create fee transaction if applicable
        if fee_amount > 0:
            fee_transaction = Transaction(
                user_id=user.id,
                amount=-fee_amount,
                type=TransactionType.FEE,
                status=TransactionStatus.COMPLETED,
                description="Wage advance fee"
            )
            self.db.add(fee_transaction)
        
        await self.db.commit()
        await self.db.refresh(advance_transaction)
        
        # Calculate new available balance
        new_balance_info = await self.get_available_wage_balance(user)
        
        return {
            "transaction_id": advance_transaction.id,
            "amount": amount,
            "fee_amount": fee_amount,
            "net_amount": net_amount,
            "status": advance_transaction.status,
            "available_balance_after": new_balance_info["available_for_advance"],
            "message": f"Successfully advanced {net_amount} (fee: {fee_amount})"
        }
    
    async def get_transaction_history(
        self,
        user_id: int,
        transaction_types: Optional[List[TransactionType]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Transaction], int]:
        """
        Get wage-related transaction history.
        
        Args:
            user_id: User ID
            transaction_types: Optional filter for transaction types
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (transactions list, total count)
        """
        # Default to wage-related types
        if transaction_types is None:
            transaction_types = [
                TransactionType.WAGE_ADVANCE,
                TransactionType.WAGE_REPAYMENT,
                TransactionType.SALARY_CREDIT,
                TransactionType.FEE
            ]
        
        # Build query
        query = select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.type.in_(transaction_types)
            )
        )
        
        # Get total count
        count_query = select(func.count(Transaction.id)).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.type.in_(transaction_types)
            )
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Transaction.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return list(transactions), total
    
    async def process_payroll_webhook(
        self,
        employer_id: str,
        employee_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming payroll webhook from employer.
        
        Args:
            employer_id: Employer identifier
            employee_id: Employee identifier
            payload: Webhook payload with payroll data
            
        Returns:
            Processing result
        """
        # Find user by employer and employee ID
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.employer_id == employer_id,
                    User.employee_id == employee_id
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                "success": False,
                "error": "User not found",
                "employer_id": employer_id,
                "employee_id": employee_id
            }
        
        # Extract payroll data
        gross_amount = Decimal(str(payload.get("gross_amount", 0)))
        net_amount = Decimal(str(payload.get("net_amount", 0)))
        days_worked = payload.get("days_worked", 0)
        reference_id = payload.get("reference_id", "")
        
        # Get pending advances to deduct
        pending_advances = await self._get_pending_advances(user.id)
        
        # Calculate daily rate from this payroll
        if days_worked > 0:
            calculated_daily_rate = gross_amount / days_worked
            # Update user's daily rate if significantly different
            if abs(calculated_daily_rate - user.daily_rate) > Decimal("10"):
                user.daily_rate = calculated_daily_rate
        
        # Create salary credit transaction
        salary_transaction = Transaction(
            user_id=user.id,
            amount=net_amount,
            type=TransactionType.SALARY_CREDIT,
            status=TransactionStatus.COMPLETED,
            reference_id=reference_id,
            description=f"Salary credit for pay period"
        )
        self.db.add(salary_transaction)
        
        # Mark pending advances as repaid
        if pending_advances > 0:
            repayment_transaction = Transaction(
                user_id=user.id,
                amount=-pending_advances,
                type=TransactionType.WAGE_REPAYMENT,
                status=TransactionStatus.COMPLETED,
                description="Automatic repayment of wage advances"
            )
            self.db.add(repayment_transaction)
        
        await self.db.commit()
        
        return {
            "success": True,
            "user_id": user.id,
            "salary_credited": net_amount,
            "advances_repaid": pending_advances,
            "reference_id": reference_id
        }
    
    async def _get_pending_advances(self, user_id: int) -> Decimal:
        """Get total pending wage advances for a user."""
        # Get current pay period
        today = datetime.now()
        
        # Sum advances in current pay period
        result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == TransactionType.WAGE_ADVANCE,
                    Transaction.status == TransactionStatus.COMPLETED,
                    Transaction.created_at >= today.replace(day=1)  # Current month
                )
            )
        )
        advances = result.scalar() or Decimal("0.00")
        
        # Subtract repayments
        result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == TransactionType.WAGE_REPAYMENT,
                    Transaction.status == TransactionStatus.COMPLETED,
                    Transaction.created_at >= today.replace(day=1)
                )
            )
        )
        repayments = abs(result.scalar() or Decimal("0.00"))
        
        return max(Decimal("0.00"), Decimal(str(advances)) - repayments)
    
    def _calculate_working_days(self, start_date: date, end_date: date) -> int:
        """Calculate working days between two dates (excluding weekends)."""
        if start_date > end_date:
            return 0
        
        working_days = 0
        current = start_date
        
        while current <= end_date:
            # Monday = 0, Sunday = 6
            if current.weekday() < 5:  # Not Saturday or Sunday
                working_days += 1
            current += timedelta(days=1)
        
        return working_days
    
    async def allocate_daily_savings_to_buckets(
        self,
        user: User,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Allocate the daily savings (Z) to user's money jars/buckets.
        
        The AI agent decides how much of Z goes into each bucket based on:
        - Bucket priorities
        - Deadlines
        - User's financial goals
        
        Args:
            user: User object
            use_ai: If True, use AI for allocation; else use proportional
            
        Returns:
            Allocation result with bucket distributions
        """
        from app.services.bucket_service import BucketService
        from app.ai.allocation_model import allocation_model
        from app.models.bucket import BucketStatus
        
        # Get daily calculations
        daily_calc = self.calculate_daily_amounts(user)
        savings_amount = daily_calc["savings_allocation"]  # Z
        
        if savings_amount <= 0:
            return {
                "success": False,
                "message": "No savings to allocate",
                "amount": 0
            }
        
        # Get user's active buckets
        bucket_service = BucketService(self.db)
        buckets = await bucket_service.get_auto_allocate_buckets(user.id)
        
        if not buckets:
            return {
                "success": False,
                "message": "No active buckets for allocation",
                "amount": float(savings_amount),
                "suggestion": "Create money jars to start auto-saving"
            }
        
        # Use AI to decide allocation
        if use_ai:
            user_profile = {
                "monthly_income": float(user.monthly_salary),
                "risk_tolerance": user.risk_tolerance,
                "tier": daily_calc["tier_number"],
                "tier_percentage": daily_calc["tier_percentage"]
            }
            
            recommendations = await allocation_model.generate_recommendations(
                amount=savings_amount,
                buckets=buckets,
                user_profile=user_profile
            )
            
            # Execute the AI recommendations
            result = await allocation_model.execute_allocation(
                allocations=recommendations["allocations"],
                buckets=buckets,
                bucket_service=bucket_service
            )
            
            result["daily_savings"] = float(savings_amount)
            result["tier_info"] = {
                "tier": daily_calc["tier_number"],
                "percentage": daily_calc["tier_percentage"]
            }
            
            return result
        
        else:
            # Proportional allocation based on bucket priorities
            total_priority = sum(11 - b.priority for b in buckets)
            allocations = []
            
            for bucket in buckets:
                weight = (11 - bucket.priority) / total_priority
                amount = savings_amount * Decimal(str(weight))
                
                # Deposit to bucket
                await bucket_service.deposit_to_bucket(
                    bucket_id=bucket.id,
                    user_id=user.id,
                    amount=amount,
                    description=f"Daily auto-save (Tier {daily_calc['tier_number']})"
                )
                
                allocations.append({
                    "bucket_id": bucket.id,
                    "bucket_name": bucket.name,
                    "amount": float(amount)
                })
            
            return {
                "success": True,
                "daily_savings": float(savings_amount),
                "allocations": allocations,
                "tier_info": {
                    "tier": daily_calc["tier_number"],
                    "percentage": daily_calc["tier_percentage"]
                },
                "message": f"Allocated {savings_amount:.2f} across {len(buckets)} buckets"
            }
    
    async def advance_user_tier(self, user: User) -> Dict[str, Any]:
        """
        Advance user to next savings tier (called monthly).
        
        Tier progression:
        - Tier 1: 20% savings (first month)
        - Tier 2: 15% savings (second month)
        - Tier 3: 5% savings (third month onwards)
        
        Args:
            user: User object
            
        Returns:
            New tier information
        """
        current_tier = user.current_savings_tier or 1
        
        if current_tier < 3:
            user.current_savings_tier = current_tier + 1
            await self.db.commit()
            await self.db.refresh(user)
        
        new_tier = user.current_savings_tier
        new_percentage = self.TIER_PERCENTAGES.get(
            min(new_tier, 3), 
            self.TIER_PERCENTAGES[3]
        )
        
        return {
            "previous_tier": current_tier,
            "new_tier": new_tier,
            "previous_percentage": float(self.TIER_PERCENTAGES.get(current_tier, self.TIER_PERCENTAGES[3]) * 100),
            "new_percentage": float(new_percentage * 100),
            "message": f"Advanced from Tier {current_tier} to Tier {new_tier}"
        }

