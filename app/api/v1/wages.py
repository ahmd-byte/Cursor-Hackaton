"""
Early Wage Access API endpoints.

Provides endpoints for wage balance checks, advances, and payroll integration.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.models.user import User
from app.models.transaction import TransactionType
from app.schemas.transaction import (
    WageAdvanceRequest,
    WageAdvanceResponse,
    WageAvailableResponse,
    PayrollWebhookPayload,
    TransactionResponse,
    TransactionListResponse,
)
from app.services.wage_service import WageService
from app.utils.security import get_current_user

router = APIRouter()


@router.get(
    "/available",
    response_model=WageAvailableResponse,
    summary="Get available wage balance",
    description="Get the current available wage balance for early access."
)
async def get_available_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> WageAvailableResponse:
    """
    Get the current user's available wage balance for early access.
    
    Returns:
    - Daily rate
    - Days worked in current pay period
    - Total earned wages
    - Available amount for advance (after deducting pending advances)
    - Maximum advance percentage
    - Next pay date
    """
    service = WageService(db)
    balance_info = await service.get_available_wage_balance(current_user)
    return WageAvailableResponse(**balance_info)


@router.post(
    "/advance",
    response_model=WageAdvanceResponse,
    summary="Request wage advance",
    description="Request early access to earned wages."
)
async def request_advance(
    request: WageAdvanceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> WageAdvanceResponse:
    """
    Request an early wage advance.
    
    - **amount**: Amount to advance (cannot exceed available balance)
    - **description**: Optional reason for the advance
    
    A processing fee may be deducted from the advance amount.
    The advance will be automatically repaid from the next salary.
    """
    service = WageService(db)
    
    try:
        result = await service.request_wage_advance(
            current_user,
            request.amount,
            request.description
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return WageAdvanceResponse(**result)


@router.get(
    "/history",
    response_model=TransactionListResponse,
    summary="Get wage transaction history",
    description="Get history of wage-related transactions."
)
async def get_wage_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> TransactionListResponse:
    """
    Get wage-related transaction history.
    
    Includes:
    - Wage advances
    - Wage repayments
    - Salary credits
    - Associated fees
    """
    service = WageService(db)
    transactions, total = await service.get_transaction_history(
        current_user.id,
        page=page,
        page_size=page_size
    )
    
    return TransactionListResponse(
        items=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post(
    "/webhook/payroll",
    summary="Payroll webhook",
    description="Webhook endpoint for employer payroll systems."
)
async def payroll_webhook(
    payload: PayrollWebhookPayload,
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Webhook endpoint for employer payroll integration.
    
    Called by employer systems when payroll is processed.
    
    - Validates employer and employee IDs
    - Credits salary to user account
    - Automatically repays any pending wage advances
    - Updates user's daily rate based on payroll data
    
    **Note**: In production, this endpoint should be secured
    with API key or webhook signature verification.
    """
    service = WageService(db)
    
    result = await service.process_payroll_webhook(
        payload.employer_id,
        payload.employee_id,
        payload.model_dump()
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Processing failed")
        )
    
    return {
        "status": "success",
        "message": "Payroll processed successfully",
        "details": result
    }


@router.get(
    "/daily-calculation",
    summary="Get daily pay calculation",
    description="Get tiered daily pay calculation with savings allocation."
)
async def get_daily_calculation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Get the tiered daily pay calculation.
    
    Formula:
    - Y (daily income) = monthly_salary / 30
    - Z (savings) = Y * tier_percentage
    - Max daily pay = Y - Z
    
    Tier percentages:
    - Month 1: 20%
    - Month 2: 15%
    - Month 3+: 5%
    
    The savings amount (Z) is automatically allocated to your money jars by AI.
    """
    service = WageService(db)
    return service.calculate_daily_amounts(current_user)


@router.post(
    "/allocate-savings",
    summary="Allocate daily savings to buckets",
    description="Trigger AI to allocate daily savings (Z) to money jars."
)
async def allocate_daily_savings(
    use_ai: bool = Query(True, description="Use AI for smart allocation"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Allocate the daily savings amount (Z) to user's money jars.
    
    The AI agent analyzes your buckets and allocates based on:
    - Bucket priorities
    - Deadlines
    - Your financial goals
    - Risk tolerance
    
    This is typically called daily or when cashing out wages.
    """
    service = WageService(db)
    
    try:
        result = await service.allocate_daily_savings_to_buckets(
            current_user,
            use_ai=use_ai
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Allocation failed: {str(e)}"
        )


@router.post(
    "/advance-tier",
    summary="Advance savings tier",
    description="Advance user to next savings tier (admin/scheduled use)."
)
async def advance_tier(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Advance user to the next savings tier.
    
    Typically called monthly by a scheduled job:
    - Tier 1 → Tier 2: 20% → 15%
    - Tier 2 → Tier 3: 15% → 5%
    - Tier 3 stays at 5%
    """
    service = WageService(db)
    return await service.advance_user_tier(current_user)


@router.get(
    "/summary",
    summary="Get wage summary",
    description="Get summary of wage advances and repayments."
)
async def get_wage_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Get summary statistics for wage advances.
    
    Returns:
    - Total advances this month
    - Total fees paid
    - Available balance
    - Days until next payday
    """
    service = WageService(db)
    
    # Get current balance info
    balance_info = await service.get_available_wage_balance(current_user)
    
    # Get transaction history for this month
    transactions, _ = await service.get_transaction_history(
        current_user.id,
        transaction_types=[
            TransactionType.WAGE_ADVANCE,
            TransactionType.FEE
        ],
        page=1,
        page_size=100
    )
    
    # Calculate totals
    from decimal import Decimal
    total_advances = sum(
        t.amount for t in transactions 
        if t.type == TransactionType.WAGE_ADVANCE
    )
    total_fees = sum(
        abs(t.amount) for t in transactions 
        if t.type == TransactionType.FEE
    )
    
    # Calculate days until payday
    from datetime import datetime
    next_pay = balance_info["next_pay_date"]
    days_until_payday = (next_pay - datetime.now()).days
    
    return {
        "total_advances_this_month": total_advances,
        "total_fees_paid": total_fees,
        "available_for_advance": balance_info["available_for_advance"],
        "earned_wages": balance_info["earned_wages"],
        "days_until_payday": max(0, days_until_payday),
        "next_pay_date": next_pay.isoformat(),
        "daily_rate": balance_info["daily_rate"],
        "days_worked": balance_info["days_worked_this_period"]
    }

