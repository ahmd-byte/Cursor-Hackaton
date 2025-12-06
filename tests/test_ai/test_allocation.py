"""
Tests for AI allocation functionality.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from app.ai.allocation_model import AllocationModel
from app.models.bucket import Bucket, BucketCategory, BucketStatus


def create_mock_bucket(
    id: int,
    name: str,
    target: Decimal,
    current: Decimal,
    priority: int = 5
) -> Bucket:
    """Create a mock bucket for testing."""
    bucket = Bucket()
    bucket.id = id
    bucket.name = name
    bucket.target_amount = target
    bucket.current_amount = current
    bucket.priority = priority
    bucket.category = BucketCategory.SAVINGS
    bucket.status = BucketStatus.ACTIVE
    bucket.auto_allocate = True
    bucket.allocation_percent = Decimal("0")
    bucket.deadline = None
    return bucket


@pytest.mark.asyncio
async def test_rule_based_allocation():
    """Test rule-based allocation fallback."""
    model = AllocationModel()
    
    buckets = [
        create_mock_bucket(1, "Emergency Fund", Decimal("10000"), Decimal("2000"), priority=1),
        create_mock_bucket(2, "Vacation", Decimal("5000"), Decimal("1000"), priority=3),
        create_mock_bucket(3, "New Car", Decimal("20000"), Decimal("5000"), priority=5),
    ]
    
    result = await model._rule_based_allocation(
        Decimal("1000"),
        buckets
    )
    
    assert "allocations" in result
    assert len(result["allocations"]) > 0
    assert result["confidence_score"] == 75
    
    # Higher priority bucket should get more
    allocations = {a["bucket_id"]: a for a in result["allocations"]}
    if 1 in allocations and 3 in allocations:
        assert allocations[1]["recommended_amount"] >= allocations[3]["recommended_amount"]


@pytest.mark.asyncio
async def test_empty_buckets():
    """Test allocation with no buckets."""
    model = AllocationModel()
    
    result = await model.generate_recommendations(
        Decimal("1000"),
        [],
        {"monthly_income": 5000}
    )
    
    assert result["allocations"] == []
    assert result["unallocated_amount"] == 1000.0
    assert "No active buckets" in result["analysis_summary"]


@pytest.mark.asyncio
async def test_urgency_calculation():
    """Test urgency level calculation."""
    model = AllocationModel()
    
    # High priority, low progress
    bucket = create_mock_bucket(1, "Test", Decimal("1000"), Decimal("100"), priority=1)
    urgency = model._calculate_urgency(bucket)
    assert urgency in ["high", "medium"]
    
    # Low priority, high progress
    bucket2 = create_mock_bucket(2, "Test2", Decimal("1000"), Decimal("900"), priority=8)
    urgency2 = model._calculate_urgency(bucket2)
    assert urgency2 == "low"


@pytest.mark.asyncio
async def test_validate_recommendations():
    """Test recommendation validation."""
    model = AllocationModel()
    
    bucket = create_mock_bucket(1, "Test", Decimal("1000"), Decimal("500"), priority=1)
    
    recommendations = {
        "allocations": [
            {
                "bucket_id": 1,
                "recommended_amount": 600,  # More than remaining
                "reasoning": "Test",
                "priority_score": 80,
                "urgency_level": "medium"
            }
        ],
        "analysis_summary": "Test",
        "confidence_score": 90,
        "factors_considered": [],
        "warnings": []
    }
    
    validated = await model._validate_recommendations(
        recommendations,
        Decimal("1000"),
        [bucket]
    )
    
    # Should cap at remaining amount (500)
    assert validated["allocations"][0]["recommended_amount"] <= 500

