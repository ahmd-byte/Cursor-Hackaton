"""
AI Agent API endpoints.

Provides endpoints for AI-powered financial analysis and recommendations.
"""

from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.models.user import User
from app.schemas.ai_allocation import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    AllocationRequest,
    AllocationResponse,
    AutoAllocateRequest,
    AutoAllocateResponse,
    AIChatRequest,
    AIChatResponse,
    FinancialHealthScore,
    SpendingAnalysis,
)
from app.services.ai_agent_service import AIAgentService
from app.utils.security import get_current_user

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AIAnalyzeResponse,
    summary="Analyze financial health",
    description="Perform comprehensive AI-powered financial analysis."
)
async def analyze_finances(
    request: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> AIAnalyzeResponse:
    """
    Perform comprehensive financial analysis using AI.
    
    - **include_spending_analysis**: Analyze spending patterns
    - **include_health_score**: Calculate financial health score
    - **include_recommendations**: Generate allocation recommendations
    - **analysis_period_days**: Number of days to analyze (7-365)
    
    Returns detailed analysis with insights and action items.
    """
    service = AIAgentService(db)
    
    try:
        result = await service.analyze_financial_health(
            user=current_user,
            include_spending=request.include_spending_analysis,
            include_health_score=request.include_health_score,
            include_recommendations=request.include_recommendations,
            period_days=request.analysis_period_days
        )
        
        return AIAnalyzeResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/recommend",
    response_model=AllocationResponse,
    summary="Get allocation recommendations",
    description="Get AI-powered recommendations for allocating funds to buckets."
)
async def get_recommendations(
    request: AllocationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> AllocationResponse:
    """
    Get smart allocation recommendations for money jars.
    
    - **amount**: Amount to allocate (optional, defaults to 20% of salary)
    - **include_analysis**: Include spending analysis in recommendations
    - **respect_priorities**: Factor in bucket priorities
    - **consider_deadlines**: Factor in deadline urgency
    
    Returns ranked recommendations with reasoning.
    """
    service = AIAgentService(db)
    
    try:
        result = await service.get_allocation_recommendations(
            user=current_user,
            amount=request.amount,
            respect_priorities=request.respect_priorities,
            consider_deadlines=request.consider_deadlines
        )
        
        return AllocationResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )


@router.post(
    "/auto-allocate",
    response_model=AutoAllocateResponse,
    summary="Execute auto-allocation",
    description="Execute AI-driven automatic fund allocation to buckets."
)
async def auto_allocate(
    request: AutoAllocateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> AutoAllocateResponse:
    """
    Execute AI-driven automatic allocation.
    
    - **amount**: Amount to allocate (optional)
    - **dry_run**: If true, returns recommendations without executing
    - **allocation_ids**: Specific bucket IDs to allocate to (optional)
    
    Creates transactions for each allocation when not in dry run mode.
    """
    service = AIAgentService(db)
    
    try:
        result = await service.execute_auto_allocation(
            user=current_user,
            amount=request.amount,
            dry_run=request.dry_run,
            bucket_ids=request.allocation_ids
        )
        
        return AutoAllocateResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-allocation failed: {str(e)}"
        )


@router.get(
    "/insights",
    summary="Get spending insights",
    description="Get AI-generated insights about spending patterns."
)
async def get_insights(
    period_days: int = Query(30, ge=7, le=365, description="Analysis period in days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Get AI-generated spending insights.
    
    Analyzes transaction history to identify:
    - Spending patterns and trends
    - Category breakdowns
    - Saving opportunities
    - Unusual transactions
    """
    service = AIAgentService(db)
    
    try:
        return await service.get_spending_insights(
            user=current_user,
            period_days=period_days
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insight generation failed: {str(e)}"
        )


@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="Chat with AI assistant",
    description="Have a conversation with the AI financial assistant."
)
async def chat_with_ai(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> AIChatResponse:
    """
    Chat with the AI financial assistant.
    
    - **message**: Your message/question
    - **conversation_history**: Previous messages for context
    - **include_financial_context**: Include your financial data as context
    
    The AI can help with:
    - Understanding your finances
    - Setting financial goals
    - Budgeting advice
    - Savings strategies
    """
    service = AIAgentService(db)
    
    try:
        # Convert conversation history
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        result = await service.chat(
            user=current_user,
            message=request.message,
            conversation_history=history,
            include_financial_context=request.include_financial_context
        )
        
        return AIChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.get(
    "/health-score",
    response_model=FinancialHealthScore,
    summary="Get financial health score",
    description="Calculate your comprehensive financial health score."
)
async def get_health_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> FinancialHealthScore:
    """
    Calculate comprehensive financial health score.
    
    Evaluates:
    - Savings rate
    - Emergency fund adequacy
    - Goal progress
    - Spending habits
    - Overall financial behavior
    
    Returns a score (0-100) with grade and personalized tips.
    """
    service = AIAgentService(db)
    
    try:
        result = await service.analyze_financial_health(
            user=current_user,
            include_spending=False,
            include_health_score=True,
            include_recommendations=False
        )
        
        if result.get("health_score"):
            return FinancialHealthScore(**result["health_score"])
        
        # Return default if no data
        return FinancialHealthScore(
            overall_score=50,
            score_breakdown={},
            grade="C",
            summary="Insufficient data to calculate accurate health score.",
            top_strengths=[],
            areas_to_improve=["Add more financial data for accurate assessment"],
            personalized_tips=["Track your expenses", "Set up savings buckets"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health score calculation failed: {str(e)}"
        )

