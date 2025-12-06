"""
AI module.

Contains AI/ML integrations with Groq and Gemini.
"""

from app.ai.groq_client import GroqClient
from app.ai.gemini_client import GeminiClient
from app.ai.allocation_model import AllocationModel
from app.ai.spending_analyzer import SpendingAnalyzer

__all__ = [
    "GroqClient",
    "GeminiClient",
    "AllocationModel",
    "SpendingAnalyzer",
]

