"""
AI allocation model for smart fund distribution.

Combines Groq's fast inference for analysis with rule-based allocation logic.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date, timedelta

from app.ai.groq_client import groq_client
from app.models.bucket import Bucket, BucketStatus


class AllocationModel:
    """
    AI-powered allocation model for distributing funds across buckets.
    
    Combines AI analysis with rule-based allocation to provide
    smart, explainable recommendations.
    """
    
    def __init__(self):
        """Initialize allocation model."""
        self.groq = groq_client
    
    async def generate_recommendations(
        self,
        amount: Decimal,
        buckets: List[Bucket],
        user_profile: Dict[str, Any],
        spending_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate allocation recommendations using AI.
        
        Args:
            amount: Total amount to allocate
            buckets: List of user's buckets
            user_profile: User's financial profile
            spending_analysis: Optional spending analysis
            
        Returns:
            Allocation recommendations with reasoning
        """
        if not buckets:
            return {
                "allocations": [],
                "unallocated_amount": float(amount),
                "analysis_summary": "No active buckets available for allocation.",
                "confidence_score": 100,
                "factors_considered": [],
                "warnings": ["Create some savings buckets to start allocating funds."]
            }
        
        # Prepare bucket data for AI
        bucket_data = []
        for bucket in buckets:
            bucket_data.append({
                "id": bucket.id,
                "name": bucket.name,
                "category": bucket.category.value,
                "target_amount": float(bucket.target_amount),
                "current_amount": float(bucket.current_amount),
                "progress_percent": bucket.progress_percent,
                "remaining_amount": float(bucket.remaining_amount),
                "priority": bucket.priority,
                "deadline": bucket.deadline.isoformat() if bucket.deadline else None,
                "days_until_deadline": bucket.days_until_deadline,
                "auto_allocate": bucket.auto_allocate,
                "allocation_percent": float(bucket.allocation_percent)
            })
        
        # Get AI recommendations
        try:
            ai_recommendations = await self.groq.generate_allocation_recommendations(
                amount=float(amount),
                buckets=bucket_data,
                user_profile=user_profile,
                spending_analysis=spending_analysis
            )
        except Exception as e:
            # Fallback to rule-based allocation if AI fails
            return await self._rule_based_allocation(amount, buckets)
        
        # Validate and adjust AI recommendations
        validated = await self._validate_recommendations(
            ai_recommendations,
            amount,
            buckets
        )
        
        return validated
    
    async def _rule_based_allocation(
        self,
        amount: Decimal,
        buckets: List[Bucket]
    ) -> Dict[str, Any]:
        """
        Fallback rule-based allocation when AI is unavailable.
        
        Priority order:
        1. Emergency fund (if < 3 months expenses)
        2. High priority buckets with close deadlines
        3. Other buckets by priority
        """
        allocations = []
        remaining = float(amount)
        
        # Sort buckets by priority and deadline
        sorted_buckets = sorted(
            buckets,
            key=lambda b: (
                b.priority,
                0 if b.days_until_deadline is None else b.days_until_deadline
            )
        )
        
        # Calculate allocation weights
        total_weight = sum(11 - b.priority for b in sorted_buckets)
        
        for bucket in sorted_buckets:
            if remaining <= 0:
                break
            
            # Calculate this bucket's share
            weight = 11 - bucket.priority
            base_allocation = (weight / total_weight) * float(amount)
            
            # Don't allocate more than remaining needed
            max_needed = float(bucket.remaining_amount)
            allocation = min(base_allocation, max_needed, remaining)
            
            if allocation > 0:
                urgency = self._calculate_urgency(bucket)
                allocations.append({
                    "bucket_id": bucket.id,
                    "bucket_name": bucket.name,
                    "recommended_amount": round(allocation, 2),
                    "percentage_of_total": round((allocation / float(amount)) * 100, 1),
                    "reasoning": f"Priority {bucket.priority} bucket with {bucket.progress_percent:.1f}% progress",
                    "priority_score": (11 - bucket.priority) * 10,
                    "urgency_level": urgency,
                    "days_to_deadline": bucket.days_until_deadline,
                    "progress_after_allocation": min(100.0, bucket.progress_percent + (allocation / float(bucket.target_amount) * 100))
                })
                remaining -= allocation
        
        return {
            "allocations": allocations,
            "unallocated_amount": round(remaining, 2),
            "analysis_summary": "Allocation based on bucket priorities and remaining amounts needed.",
            "confidence_score": 75,
            "factors_considered": ["bucket_priority", "remaining_amount", "deadline"],
            "warnings": []
        }
    
    async def _validate_recommendations(
        self,
        recommendations: Dict[str, Any],
        amount: Decimal,
        buckets: List[Bucket]
    ) -> Dict[str, Any]:
        """
        Validate and adjust AI recommendations.
        
        Ensures:
        - Total doesn't exceed available amount
        - Individual allocations don't exceed bucket needs
        - All bucket IDs are valid
        """
        bucket_map = {b.id: b for b in buckets}
        validated_allocations = []
        total_allocated = Decimal("0")
        
        for alloc in recommendations.get("allocations", []):
            bucket_id = alloc.get("bucket_id")
            recommended = Decimal(str(alloc.get("recommended_amount", 0)))
            
            # Skip invalid bucket IDs
            if bucket_id not in bucket_map:
                continue
            
            bucket = bucket_map[bucket_id]
            
            # Don't allocate more than needed
            max_needed = bucket.remaining_amount
            adjusted = min(recommended, max_needed, amount - total_allocated)
            
            if adjusted > 0:
                total_allocated += adjusted
                
                validated_allocations.append({
                    "bucket_id": bucket_id,
                    "bucket_name": bucket.name,
                    "recommended_amount": float(adjusted),
                    "percentage_of_total": float((adjusted / amount) * 100) if amount > 0 else 0,
                    "reasoning": alloc.get("reasoning", ""),
                    "priority_score": alloc.get("priority_score", 50),
                    "urgency_level": alloc.get("urgency_level", "medium"),
                    "days_to_deadline": bucket.days_until_deadline,
                    "progress_after_allocation": min(100.0, bucket.progress_percent + float(adjusted / bucket.target_amount * 100))
                })
        
        return {
            "allocations": validated_allocations,
            "unallocated_amount": float(amount - total_allocated),
            "analysis_summary": recommendations.get("analysis_summary", ""),
            "confidence_score": recommendations.get("confidence_score", 80),
            "factors_considered": recommendations.get("factors_considered", []),
            "warnings": recommendations.get("warnings", [])
        }
    
    def _calculate_urgency(self, bucket: Bucket) -> str:
        """Calculate urgency level for a bucket."""
        # Critical if deadline is within 7 days and not complete
        if bucket.days_until_deadline is not None:
            if bucket.days_until_deadline <= 7 and bucket.progress_percent < 90:
                return "critical"
            elif bucket.days_until_deadline <= 30 and bucket.progress_percent < 75:
                return "high"
            elif bucket.days_until_deadline <= 90 and bucket.progress_percent < 50:
                return "medium"
        
        # High priority buckets
        if bucket.priority <= 2:
            return "high" if bucket.progress_percent < 50 else "medium"
        
        return "low"
    
    async def execute_allocation(
        self,
        allocations: List[Dict[str, Any]],
        buckets: List[Bucket],
        bucket_service
    ) -> Dict[str, Any]:
        """
        Execute the recommended allocations.
        
        Args:
            allocations: List of allocation recommendations
            buckets: List of bucket objects
            bucket_service: BucketService instance for deposits
            
        Returns:
            Execution result with transaction details
        """
        bucket_map = {b.id: b for b in buckets}
        results = []
        total_allocated = Decimal("0")
        errors = []
        
        for alloc in allocations:
            bucket_id = alloc["bucket_id"]
            amount = Decimal(str(alloc["recommended_amount"]))
            
            if bucket_id not in bucket_map:
                errors.append(f"Bucket {bucket_id} not found")
                continue
            
            try:
                bucket = await bucket_service.deposit_to_bucket(
                    bucket_id=bucket_id,
                    user_id=bucket_map[bucket_id].user_id,
                    amount=amount,
                    description=f"AI auto-allocation: {alloc.get('reasoning', '')[:100]}"
                )
                
                if bucket:
                    results.append({
                        "bucket_id": bucket_id,
                        "bucket_name": bucket.name,
                        "amount_allocated": float(amount),
                        "new_balance": float(bucket.current_amount),
                        "success": True
                    })
                    total_allocated += amount
                else:
                    errors.append(f"Failed to deposit to bucket {bucket_id}")
                    
            except Exception as e:
                errors.append(f"Error allocating to {bucket_id}: {str(e)}")
        
        return {
            "success": len(errors) == 0,
            "total_allocated": float(total_allocated),
            "transactions_created": len(results),
            "allocations": results,
            "errors": errors,
            "message": f"Successfully allocated {total_allocated} to {len(results)} buckets" if results else "No allocations made"
        }


# Singleton instance
allocation_model = AllocationModel()

