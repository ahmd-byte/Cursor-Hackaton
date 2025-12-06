"""
AI Agent service for orchestrating AI-powered financial operations.

Uses LangChain to combine Groq and Gemini capabilities for
comprehensive financial analysis and recommendations.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config import settings
from app.models.user import User
from app.models.bucket import Bucket, BucketStatus
from app.models.transaction import Transaction
from app.ai.groq_client import groq_client
from app.ai.gemini_client import gemini_client
from app.ai.allocation_model import allocation_model
from app.ai.spending_analyzer import spending_analyzer
from app.services.bucket_service import BucketService


class AIAgentService:
    """
    AI Agent service for comprehensive financial AI operations.
    
    Orchestrates between different AI models and services to provide:
    - Financial analysis and insights
    - Smart allocation recommendations
    - Spending pattern analysis
    - Interactive financial assistance
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize AI agent service with database session."""
        self.db = db
        self.groq = groq_client
        self.gemini = gemini_client
        self.allocation_model = allocation_model
        self.spending_analyzer = spending_analyzer
        
        # Initialize LangChain models
        self._groq_llm = None
        self._gemini_llm = None
        self._agent = None
    
    @property
    def groq_llm(self):
        """Get or create LangChain Groq model."""
        if self._groq_llm is None and settings.groq_api_key:
            self._groq_llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.groq_model,
                temperature=settings.groq_temperature
            )
        return self._groq_llm
    
    @property
    def gemini_llm(self):
        """Get or create LangChain Gemini model."""
        if self._gemini_llm is None and settings.gemini_api_key:
            self._gemini_llm = ChatGoogleGenerativeAI(
                google_api_key=settings.gemini_api_key,
                model=settings.gemini_model,
                temperature=settings.gemini_temperature
            )
        return self._gemini_llm
    
    async def analyze_financial_health(
        self,
        user: User,
        include_spending: bool = True,
        include_health_score: bool = True,
        include_recommendations: bool = True,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial health analysis.
        
        Args:
            user: User to analyze
            include_spending: Include spending analysis
            include_health_score: Include health score calculation
            include_recommendations: Include allocation recommendations
            period_days: Analysis period in days
            
        Returns:
            Comprehensive financial analysis
        """
        result = {
            "user_id": user.id,
            "generated_at": datetime.utcnow(),
            "spending_analysis": None,
            "health_score": None,
            "allocation_recommendations": None,
            "insights": [],
            "action_items": []
        }
        
        # Get user's transactions
        transactions = await self._get_user_transactions(user.id, period_days)
        
        # Get user's buckets
        buckets = await self._get_user_buckets(user.id)
        buckets_data = [
            {
                "id": b.id,
                "name": b.name,
                "target_amount": float(b.target_amount),
                "current_amount": float(b.current_amount),
                "progress_percent": b.progress_percent,
                "priority": b.priority,
                "category": b.category.value
            }
            for b in buckets
        ]
        
        # User context
        user_context = {
            "monthly_salary": float(user.monthly_salary),
            "daily_rate": float(user.daily_rate),
            "risk_tolerance": user.risk_tolerance,
            "financial_goals": user.financial_goals
        }
        
        # Spending analysis
        if include_spending:
            result["spending_analysis"] = await self.spending_analyzer.analyze_spending_patterns(
                transactions=transactions,
                user_context=user_context,
                period_days=period_days
            )
            result["insights"].extend(
                result["spending_analysis"].get("insights", [])
            )
        
        # Health score
        if include_health_score:
            result["health_score"] = await self.spending_analyzer.calculate_financial_health(
                user_data=user_context,
                transactions=transactions,
                buckets_data=buckets_data
            )
            # Add action items from health score
            result["action_items"].extend(
                result["health_score"].get("personalized_tips", [])
            )
        
        # Allocation recommendations
        if include_recommendations and buckets:
            # Calculate available amount for allocation
            available = float(user.monthly_salary) * 0.2  # 20% of salary as example
            
            result["allocation_recommendations"] = await self.allocation_model.generate_recommendations(
                amount=Decimal(str(available)),
                buckets=buckets,
                user_profile=user_context,
                spending_analysis=result.get("spending_analysis")
            )
        
        return result
    
    async def get_allocation_recommendations(
        self,
        user: User,
        amount: Optional[Decimal] = None,
        respect_priorities: bool = True,
        consider_deadlines: bool = True
    ) -> Dict[str, Any]:
        """
        Get AI-powered allocation recommendations.
        
        Args:
            user: User requesting recommendations
            amount: Amount to allocate (defaults to 20% of salary)
            respect_priorities: Factor in bucket priorities
            consider_deadlines: Factor in deadline urgency
            
        Returns:
            Allocation recommendations
        """
        # Get user's active buckets
        buckets = await self._get_user_buckets(user.id, active_only=True)
        
        if not buckets:
            return {
                "total_amount": 0,
                "allocations": [],
                "unallocated_amount": float(amount or 0),
                "analysis_summary": "No active buckets available for allocation.",
                "confidence_score": 100,
                "factors_considered": [],
                "warnings": ["Create savings buckets to receive allocation recommendations."],
                "generated_at": datetime.utcnow()
            }
        
        # Default amount to 20% of monthly salary
        if amount is None:
            amount = user.monthly_salary * Decimal("0.2")
        
        # Get recent spending analysis
        transactions = await self._get_user_transactions(user.id, 30)
        spending_analysis = None
        if transactions:
            spending_analysis = await self.spending_analyzer.analyze_spending_patterns(
                transactions=transactions,
                user_context={"monthly_salary": float(user.monthly_salary)},
                period_days=30
            )
        
        # User profile for AI
        user_profile = {
            "monthly_income": float(user.monthly_salary),
            "risk_tolerance": user.risk_tolerance,
            "financial_goals": user.financial_goals,
            "respect_priorities": respect_priorities,
            "consider_deadlines": consider_deadlines
        }
        
        # Generate recommendations
        recommendations = await self.allocation_model.generate_recommendations(
            amount=amount,
            buckets=buckets,
            user_profile=user_profile,
            spending_analysis=spending_analysis
        )
        
        recommendations["total_amount"] = float(amount)
        recommendations["generated_at"] = datetime.utcnow()
        
        return recommendations
    
    async def execute_auto_allocation(
        self,
        user: User,
        amount: Optional[Decimal] = None,
        dry_run: bool = False,
        bucket_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Execute AI-driven auto-allocation.
        
        Args:
            user: User executing allocation
            amount: Amount to allocate
            dry_run: If True, return recommendations without executing
            bucket_ids: Optional specific bucket IDs to allocate to
            
        Returns:
            Allocation execution result
        """
        # Get recommendations
        recommendations = await self.get_allocation_recommendations(
            user=user,
            amount=amount
        )
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "total_allocated": 0,
                "transactions_created": 0,
                "allocations": recommendations["allocations"],
                "errors": [],
                "message": "Dry run - no changes made"
            }
        
        # Filter by specific bucket IDs if provided
        allocations = recommendations["allocations"]
        if bucket_ids:
            allocations = [a for a in allocations if a["bucket_id"] in bucket_ids]
        
        if not allocations:
            return {
                "success": True,
                "total_allocated": 0,
                "transactions_created": 0,
                "allocations": [],
                "errors": [],
                "message": "No allocations to execute"
            }
        
        # Get buckets for execution
        buckets = await self._get_user_buckets(user.id)
        bucket_service = BucketService(self.db)
        
        # Execute allocations
        result = await self.allocation_model.execute_allocation(
            allocations=allocations,
            buckets=buckets,
            bucket_service=bucket_service
        )
        
        return result
    
    async def get_spending_insights(
        self,
        user: User,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get AI-generated spending insights.
        
        Args:
            user: User to analyze
            period_days: Analysis period
            
        Returns:
            Spending insights and recommendations
        """
        transactions = await self._get_user_transactions(user.id, period_days)
        
        user_context = {
            "monthly_salary": float(user.monthly_salary),
            "risk_tolerance": user.risk_tolerance
        }
        
        analysis = await self.spending_analyzer.analyze_spending_patterns(
            transactions=transactions,
            user_context=user_context,
            period_days=period_days
        )
        
        return {
            "period_days": period_days,
            "total_transactions": len(transactions),
            "spending_analysis": analysis,
            "generated_at": datetime.utcnow()
        }
    
    async def chat(
        self,
        user: User,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        include_financial_context: bool = True
    ) -> Dict[str, Any]:
        """
        Have an AI chat conversation about finances.
        
        Args:
            user: User chatting
            message: User's message
            conversation_history: Previous messages
            include_financial_context: Include user's financial data
            
        Returns:
            AI response with suggestions
        """
        # Build financial context
        financial_context = None
        if include_financial_context:
            buckets = await self._get_user_buckets(user.id)
            transactions = await self._get_user_transactions(user.id, 30)
            
            financial_context = {
                "monthly_salary": float(user.monthly_salary),
                "daily_rate": float(user.daily_rate),
                "num_buckets": len(buckets),
                "total_saved": sum(float(b.current_amount) for b in buckets),
                "recent_transactions": len(transactions),
                "buckets": [
                    {
                        "name": b.name,
                        "progress": f"{b.progress_percent:.1f}%",
                        "category": b.category.value
                    }
                    for b in buckets[:5]
                ]
            }
        
        # Get AI response
        history = conversation_history or []
        response = await self.groq.chat(
            message=message,
            conversation_history=history,
            financial_context=financial_context
        )
        
        # Extract any suggested actions
        suggested_actions = []
        action_keywords = ["should", "recommend", "suggest", "try", "consider"]
        for sentence in response.split("."):
            if any(kw in sentence.lower() for kw in action_keywords):
                action = sentence.strip()
                if action and len(action) > 10:
                    suggested_actions.append(action)
        
        return {
            "message": response,
            "suggested_actions": suggested_actions[:3],
            "related_insights": [],
            "confidence": 85.0
        }
    
    async def _get_user_transactions(
        self,
        user_id: int,
        days: int
    ) -> List[Transaction]:
        """Get user's recent transactions."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.created_at >= cutoff)
            .order_by(Transaction.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def _get_user_buckets(
        self,
        user_id: int,
        active_only: bool = False
    ) -> List[Bucket]:
        """Get user's buckets."""
        query = select(Bucket).where(Bucket.user_id == user_id)
        
        if active_only:
            query = query.where(Bucket.status == BucketStatus.ACTIVE)
            query = query.where(Bucket.auto_allocate == True)
        
        query = query.order_by(Bucket.priority.asc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

