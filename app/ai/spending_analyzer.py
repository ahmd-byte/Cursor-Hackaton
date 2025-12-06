"""
Spending pattern analyzer using AI.

Analyzes transaction history to identify patterns and provide insights.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.ai.groq_client import groq_client
from app.models.transaction import Transaction, TransactionType


class SpendingAnalyzer:
    """
    AI-powered spending pattern analyzer.
    
    Analyzes transaction history to:
    - Identify spending patterns
    - Categorize expenses
    - Find saving opportunities
    - Calculate financial health metrics
    """
    
    def __init__(self):
        """Initialize spending analyzer."""
        self.groq = groq_client
    
    async def analyze_spending_patterns(
        self,
        transactions: List[Transaction],
        user_context: Optional[Dict[str, Any]] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze spending patterns from transaction history.
        
        Args:
            transactions: List of user's transactions
            user_context: Optional context about user (income, goals)
            period_days: Number of days to analyze
            
        Returns:
            Comprehensive spending analysis
        """
        # Filter transactions to analysis period
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        recent_transactions = [
            t for t in transactions
            if t.created_at >= cutoff_date
        ]
        
        if not recent_transactions:
            return self._empty_analysis(period_days)
        
        # Calculate basic metrics
        basic_metrics = self._calculate_basic_metrics(recent_transactions)
        
        # Prepare transaction data for AI analysis
        transaction_data = [
            {
                "date": t.created_at.isoformat(),
                "amount": float(t.amount),
                "type": t.type.value,
                "description": t.description or "",
                "category": self._infer_category(t)
            }
            for t in recent_transactions
        ]
        
        # Get AI analysis
        try:
            ai_analysis = await self.groq.analyze_spending(
                transactions=transaction_data,
                user_context=user_context
            )
        except Exception:
            ai_analysis = {}
        
        # Combine basic metrics with AI insights
        return {
            "analysis_period_start": cutoff_date,
            "analysis_period_end": datetime.utcnow(),
            "total_income": basic_metrics["total_income"],
            "total_expenses": basic_metrics["total_expenses"],
            "net_savings": basic_metrics["net_savings"],
            "savings_rate": basic_metrics["savings_rate"],
            "spending_by_category": ai_analysis.get(
                "spending_by_category",
                basic_metrics["spending_by_type"]
            ),
            "income_by_source": basic_metrics.get("income_by_source", {}),
            "average_daily_spending": basic_metrics["average_daily_spending"],
            "highest_spending_day": ai_analysis.get("highest_spending_day"),
            "lowest_spending_day": ai_analysis.get("lowest_spending_day"),
            "spending_trend": ai_analysis.get("spending_trend", "stable"),
            "insights": self._generate_insights(basic_metrics, ai_analysis),
            "areas_for_improvement": ai_analysis.get("savings_opportunities", []),
            "positive_behaviors": ai_analysis.get("recommendations", [])[:3]
        }
    
    async def calculate_financial_health(
        self,
        user_data: Dict[str, Any],
        transactions: List[Transaction],
        buckets_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive financial health score.
        
        Args:
            user_data: User's profile data
            transactions: Transaction history
            buckets_data: User's savings buckets data
            
        Returns:
            Financial health score with breakdown
        """
        # Prepare comprehensive user data
        analysis_data = {
            "monthly_income": float(user_data.get("monthly_salary", 0)),
            "risk_tolerance": user_data.get("risk_tolerance", 5),
            "transaction_summary": self._summarize_transactions(transactions),
            "savings_goals": buckets_data,
            "total_saved": sum(b.get("current_amount", 0) for b in buckets_data),
            "total_goal_amount": sum(b.get("target_amount", 0) for b in buckets_data),
            "goals_progress": self._calculate_goals_progress(buckets_data)
        }
        
        try:
            health_score = await self.groq.calculate_financial_health_score(analysis_data)
            return health_score
        except Exception:
            # Fallback to rule-based scoring
            return self._rule_based_health_score(analysis_data)
    
    def _calculate_basic_metrics(
        self,
        transactions: List[Transaction]
    ) -> Dict[str, Any]:
        """Calculate basic financial metrics from transactions."""
        total_income = Decimal("0")
        total_expenses = Decimal("0")
        spending_by_type = defaultdict(Decimal)
        daily_spending = defaultdict(Decimal)
        
        for t in transactions:
            if t.amount > 0:
                total_income += t.amount
            else:
                total_expenses += abs(t.amount)
                spending_by_type[t.type.value] += abs(t.amount)
                daily_spending[t.created_at.date()] += abs(t.amount)
        
        # Calculate savings rate
        savings_rate = 0.0
        if total_income > 0:
            savings_rate = float((total_income - total_expenses) / total_income * 100)
        
        # Calculate average daily spending
        num_days = len(daily_spending) or 1
        avg_daily = total_expenses / num_days
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": total_income - total_expenses,
            "savings_rate": savings_rate,
            "spending_by_type": dict(spending_by_type),
            "average_daily_spending": avg_daily
        }
    
    def _infer_category(self, transaction: Transaction) -> str:
        """Infer category from transaction type and description."""
        type_categories = {
            TransactionType.WAGE_ADVANCE: "income",
            TransactionType.SALARY_CREDIT: "income",
            TransactionType.BUCKET_DEPOSIT: "savings",
            TransactionType.BUCKET_WITHDRAWAL: "withdrawal",
            TransactionType.AUTO_ALLOCATION: "savings",
            TransactionType.FEE: "fees"
        }
        return type_categories.get(transaction.type, "other")
    
    def _summarize_transactions(
        self,
        transactions: List[Transaction]
    ) -> Dict[str, Any]:
        """Create a summary of transaction history."""
        if not transactions:
            return {"total": 0, "by_type": {}}
        
        by_type = defaultdict(int)
        total_amount = Decimal("0")
        
        for t in transactions:
            by_type[t.type.value] += 1
            total_amount += t.amount
        
        return {
            "total_transactions": len(transactions),
            "total_amount": float(total_amount),
            "by_type": dict(by_type)
        }
    
    def _calculate_goals_progress(
        self,
        buckets: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall progress towards financial goals."""
        if not buckets:
            return 0.0
        
        total_target = sum(b.get("target_amount", 0) for b in buckets)
        total_current = sum(b.get("current_amount", 0) for b in buckets)
        
        if total_target == 0:
            return 100.0
        
        return (total_current / total_target) * 100
    
    def _generate_insights(
        self,
        basic_metrics: Dict[str, Any],
        ai_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate financial insights from analysis."""
        insights = []
        
        # Savings rate insight
        savings_rate = basic_metrics.get("savings_rate", 0)
        if savings_rate >= 20:
            insights.append({
                "category": "saving",
                "title": "Great Savings Rate",
                "description": f"You're saving {savings_rate:.1f}% of your income, which is excellent!",
                "importance": "high",
                "actionable": False,
                "suggested_action": None,
                "related_bucket_ids": [],
                "data_points": {"savings_rate": savings_rate}
            })
        elif savings_rate < 10:
            insights.append({
                "category": "saving",
                "title": "Low Savings Rate",
                "description": f"Your savings rate is {savings_rate:.1f}%. Consider increasing to at least 10-15%.",
                "importance": "high",
                "actionable": True,
                "suggested_action": "Review your expenses and identify areas to cut back",
                "related_bucket_ids": [],
                "data_points": {"savings_rate": savings_rate}
            })
        
        # Add AI-generated insights
        for risk in ai_analysis.get("risk_flags", []):
            insights.append({
                "category": "warning",
                "title": "Financial Risk",
                "description": risk,
                "importance": "high",
                "actionable": True,
                "suggested_action": "Address this issue promptly",
                "related_bucket_ids": [],
                "data_points": {}
            })
        
        return insights
    
    def _rule_based_health_score(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback rule-based health score calculation."""
        scores = {}
        
        # Savings score (0-100)
        savings_ratio = data.get("total_saved", 0) / max(data.get("monthly_income", 1), 1)
        scores["savings"] = min(100, int(savings_ratio * 50))
        
        # Goal progress score
        scores["goal_progress"] = int(data.get("goals_progress", 0))
        
        # Overall score (average)
        overall = sum(scores.values()) // len(scores) if scores else 50
        
        # Determine grade
        grades = [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "F")]
        grade = next(g for threshold, g in grades if overall >= threshold)
        
        return {
            "overall_score": overall,
            "grade": grade,
            "score_breakdown": scores,
            "summary": f"Your financial health score is {overall}/100 ({grade})",
            "top_strengths": ["Regular savings habit"] if scores.get("savings", 0) > 50 else [],
            "areas_to_improve": ["Increase savings rate"] if scores.get("savings", 0) < 50 else [],
            "personalized_tips": [
                "Set up automatic transfers to savings",
                "Review subscriptions monthly",
                "Track all expenses for a week"
            ]
        }
    
    def _empty_analysis(self, period_days: int) -> Dict[str, Any]:
        """Return empty analysis when no transactions available."""
        return {
            "analysis_period_start": datetime.utcnow() - timedelta(days=period_days),
            "analysis_period_end": datetime.utcnow(),
            "total_income": Decimal("0"),
            "total_expenses": Decimal("0"),
            "net_savings": Decimal("0"),
            "savings_rate": 0.0,
            "spending_by_category": {},
            "income_by_source": {},
            "average_daily_spending": Decimal("0"),
            "highest_spending_day": None,
            "lowest_spending_day": None,
            "spending_trend": "stable",
            "insights": [{
                "category": "info",
                "title": "No Transaction Data",
                "description": f"No transactions found in the last {period_days} days.",
                "importance": "low",
                "actionable": False,
                "suggested_action": None,
                "related_bucket_ids": [],
                "data_points": {}
            }],
            "areas_for_improvement": [],
            "positive_behaviors": []
        }


# Singleton instance
spending_analyzer = SpendingAnalyzer()

