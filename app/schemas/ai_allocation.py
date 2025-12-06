"""
AI allocation and analysis related Pydantic schemas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AllocationRequest(BaseModel):
    """Schema for AI allocation request."""
    
    amount: Optional[Decimal] = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Amount to allocate (uses available balance if not specified)"
    )
    include_analysis: bool = Field(
        default=True,
        description="Include spending analysis in response"
    )
    respect_priorities: bool = Field(
        default=True,
        description="Prioritize buckets by their priority setting"
    )
    consider_deadlines: bool = Field(
        default=True,
        description="Factor in bucket deadlines"
    )


class AllocationRecommendation(BaseModel):
    """Schema for a single bucket allocation recommendation."""
    
    bucket_id: int
    bucket_name: str
    recommended_amount: Decimal
    percentage_of_total: float
    reasoning: str
    priority_score: float = Field(description="AI-calculated priority score (0-100)")
    urgency_level: str = Field(description="low, medium, high, critical")
    days_to_deadline: Optional[int] = None
    progress_after_allocation: float


class AllocationResponse(BaseModel):
    """Schema for AI allocation response."""
    
    total_amount: Decimal
    allocations: List[AllocationRecommendation]
    unallocated_amount: Decimal
    analysis_summary: Optional[str] = None
    confidence_score: float = Field(description="AI confidence in recommendations (0-100)")
    generated_at: datetime
    
    # Metadata about the allocation decision
    factors_considered: List[str] = []
    warnings: List[str] = []


class FinancialInsight(BaseModel):
    """Schema for a single financial insight."""
    
    category: str = Field(description="Category of insight (spending, saving, goal, etc.)")
    title: str
    description: str
    importance: str = Field(description="low, medium, high")
    actionable: bool
    suggested_action: Optional[str] = None
    related_bucket_ids: List[int] = []
    data_points: Dict[str, Any] = {}


class SpendingAnalysis(BaseModel):
    """Schema for spending pattern analysis."""
    
    analysis_period_start: datetime
    analysis_period_end: datetime
    total_income: Decimal
    total_expenses: Decimal
    net_savings: Decimal
    savings_rate: float = Field(description="Percentage of income saved")
    
    # Category breakdown
    spending_by_category: Dict[str, Decimal] = {}
    income_by_source: Dict[str, Decimal] = {}
    
    # Patterns
    average_daily_spending: Decimal
    highest_spending_day: Optional[str] = None
    lowest_spending_day: Optional[str] = None
    spending_trend: str = Field(description="increasing, decreasing, stable")
    
    # Recommendations
    insights: List[FinancialInsight] = []
    areas_for_improvement: List[str] = []
    positive_behaviors: List[str] = []


class FinancialHealthScore(BaseModel):
    """Schema for overall financial health score."""
    
    overall_score: int = Field(ge=0, le=100, description="Overall financial health (0-100)")
    score_breakdown: Dict[str, int] = Field(
        description="Scores for different aspects (savings, debt, goals, etc.)"
    )
    grade: str = Field(description="A, B, C, D, F grade")
    summary: str
    top_strengths: List[str] = []
    areas_to_improve: List[str] = []
    personalized_tips: List[str] = []
    compared_to_peers: Optional[str] = None


class AIAnalyzeRequest(BaseModel):
    """Schema for AI analysis request."""
    
    include_spending_analysis: bool = True
    include_health_score: bool = True
    include_recommendations: bool = True
    analysis_period_days: int = Field(default=30, ge=7, le=365)


class AIAnalyzeResponse(BaseModel):
    """Schema for AI analysis response."""
    
    user_id: int
    generated_at: datetime
    spending_analysis: Optional[SpendingAnalysis] = None
    health_score: Optional[FinancialHealthScore] = None
    allocation_recommendations: Optional[AllocationResponse] = None
    insights: List[FinancialInsight] = []
    action_items: List[str] = []


class AutoAllocateRequest(BaseModel):
    """Schema for executing auto-allocation."""
    
    amount: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Amount to allocate (uses available balance if not specified)"
    )
    dry_run: bool = Field(
        default=False,
        description="If true, returns recommendations without executing"
    )
    allocation_ids: Optional[List[int]] = Field(
        None,
        description="Specific bucket IDs to allocate to (all eligible if not specified)"
    )


class AutoAllocateResponse(BaseModel):
    """Schema for auto-allocation execution response."""
    
    success: bool
    total_allocated: Decimal
    transactions_created: int
    allocations: List[AllocationRecommendation]
    errors: List[str] = []
    message: str


class ChatMessage(BaseModel):
    """Schema for AI chat message."""
    
    role: str = Field(description="user or assistant")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIChatRequest(BaseModel):
    """Schema for AI chat request."""
    
    message: str = Field(..., max_length=2000, description="User's message")
    conversation_history: List[ChatMessage] = Field(
        default=[],
        max_length=20,
        description="Previous messages in conversation"
    )
    include_financial_context: bool = Field(
        default=True,
        description="Include user's financial data as context"
    )


class AIChatResponse(BaseModel):
    """Schema for AI chat response."""
    
    message: str
    suggested_actions: List[str] = []
    related_insights: List[FinancialInsight] = []
    confidence: float

