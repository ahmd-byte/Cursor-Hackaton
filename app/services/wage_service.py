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
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
    
    async def get_available_wage_balance(self, user: User) -> Dict[str, Any]:
        """
        Calculate the available wage balance for early access.
        
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
        
        # Calculate earned wages
        daily_rate = user.daily_rate or Decimal("0.00")
        earned_wages = daily_rate * days_worked
        
        # Get pending advances
        pending_advances = await self._get_pending_advances(user.id)
        
        # Calculate available for advance
        max_percent = Decimal(str(settings.max_wage_advance_percent)) / Decimal("100")
        max_available = earned_wages * max_percent
        available_for_advance = max(Decimal("0.00"), max_available - pending_advances)
        
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
            "daily_rate": daily_rate,
            "days_worked_this_period": days_worked,
            "earned_wages": earned_wages,
            "available_for_advance": available_for_advance,
            "max_advance_percent": float(settings.max_wage_advance_percent),
            "pending_advances": pending_advances,
            "next_pay_date": next_pay
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

