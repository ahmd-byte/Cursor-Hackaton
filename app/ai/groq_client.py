"""
Groq API client for fast AI inference.

Provides wrapper for Groq's ultra-fast language model API.
"""

import json
from typing import Optional, List, Dict, Any
from groq import Groq, AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings


class GroqClient:
    """
    Client for Groq API interactions.
    
    Groq provides extremely fast inference for language models,
    making it ideal for real-time financial analysis and recommendations.
    """
    
    def __init__(self):
        """Initialize Groq client with API key from settings."""
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.max_tokens = settings.groq_max_tokens
        self.temperature = settings.groq_temperature
        
        # Initialize async client
        self._client = None
    
    @property
    def client(self) -> AsyncGroq:
        """Get or create async Groq client."""
        if self._client is None:
            self._client = AsyncGroq(api_key=self.api_key)
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate text using Groq's language model.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: If True, response will be valid JSON
            
        Returns:
            Generated text response
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response_format = {"type": "json_object"} if json_mode else None
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            response_format=response_format
        )
        
        return response.choices[0].message.content
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            schema_hint: Optional JSON schema hint for the output
            
        Returns:
            Parsed JSON dictionary
        """
        full_system = system_prompt or ""
        if schema_hint:
            full_system += f"\n\nExpected JSON schema:\n{schema_hint}"
        full_system += "\n\nRespond only with valid JSON."
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=full_system,
            json_mode=True
        )
        
        return json.loads(response)
    
    async def analyze_spending(
        self,
        transactions: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze spending patterns from transaction data.
        
        Args:
            transactions: List of transaction dictionaries
            user_context: Optional user context (income, goals, etc.)
            
        Returns:
            Analysis results with patterns and recommendations
        """
        system_prompt = """You are a financial analyst AI assistant.
Analyze the provided transaction data and identify spending patterns,
categorize expenses, and provide actionable insights.

Be specific with numbers and percentages.
Focus on practical, actionable recommendations."""
        
        context_str = ""
        if user_context:
            context_str = f"\n\nUser Context:\n{json.dumps(user_context, indent=2)}"
        
        prompt = f"""Analyze these transactions and provide spending insights:

Transactions:
{json.dumps(transactions, indent=2)}
{context_str}

Provide your analysis in the following JSON format:
{{
    "total_spending": <number>,
    "spending_by_category": {{"category": amount}},
    "top_spending_categories": ["category1", "category2", "category3"],
    "spending_trend": "increasing|decreasing|stable",
    "average_daily_spending": <number>,
    "unusual_transactions": [<list of unusual transactions>],
    "savings_opportunities": ["opportunity1", "opportunity2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "risk_flags": ["flag1", "flag2"]
}}"""
        
        return await self.generate_json(prompt, system_prompt)
    
    async def generate_allocation_recommendations(
        self,
        amount: float,
        buckets: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        spending_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate smart allocation recommendations for money jars.
        
        Args:
            amount: Amount to allocate
            buckets: List of bucket dictionaries
            user_profile: User's financial profile
            spending_analysis: Optional recent spending analysis
            
        Returns:
            Allocation recommendations
        """
        system_prompt = """You are a financial planning AI assistant.
Your task is to recommend optimal allocation of funds across savings buckets/goals.

Consider:
1. Bucket priorities (1 = highest priority)
2. Deadline urgency (closer deadlines need more attention)
3. Current progress (buckets far from goal need more)
4. User's risk tolerance
5. Overall financial health

Be practical and explain your reasoning briefly."""
        
        spending_str = ""
        if spending_analysis:
            spending_str = f"\n\nRecent Spending Analysis:\n{json.dumps(spending_analysis, indent=2)}"
        
        prompt = f"""Recommend how to allocate ${amount:.2f} across these savings buckets:

Buckets:
{json.dumps(buckets, indent=2)}

User Profile:
{json.dumps(user_profile, indent=2)}
{spending_str}

Provide your recommendations in this JSON format:
{{
    "allocations": [
        {{
            "bucket_id": <id>,
            "bucket_name": "<name>",
            "recommended_amount": <amount>,
            "percentage_of_total": <percentage>,
            "reasoning": "<brief explanation>",
            "priority_score": <0-100>,
            "urgency_level": "low|medium|high|critical"
        }}
    ],
    "unallocated_amount": <amount>,
    "analysis_summary": "<overall summary>",
    "confidence_score": <0-100>,
    "factors_considered": ["factor1", "factor2"],
    "warnings": ["warning1 if any"]
}}"""
        
        return await self.generate_json(prompt, system_prompt)
    
    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        financial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Have a conversation about finances.
        
        Args:
            message: User's message
            conversation_history: Previous messages in conversation
            financial_context: User's financial data for context
            
        Returns:
            AI response
        """
        system_prompt = """You are a helpful financial assistant AI.
You help users understand their finances, set goals, and make smart decisions.
Be friendly, clear, and practical in your advice.
When discussing money, always be specific with numbers when you have them."""
        
        if financial_context:
            system_prompt += f"\n\nUser's Financial Context:\n{json.dumps(financial_context, indent=2)}"
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def calculate_financial_health_score(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate a comprehensive financial health score.
        
        Args:
            user_data: User's financial data
            
        Returns:
            Health score with breakdown and recommendations
        """
        system_prompt = """You are a financial health analyst.
Calculate a comprehensive financial health score (0-100) based on the user's data.

Consider:
- Savings rate (percentage of income saved)
- Emergency fund adequacy
- Debt-to-income ratio
- Goal progress
- Spending habits
- Financial behaviors"""
        
        prompt = f"""Calculate the financial health score for this user:

User Financial Data:
{json.dumps(user_data, indent=2)}

Provide the score in this JSON format:
{{
    "overall_score": <0-100>,
    "grade": "A|B|C|D|F",
    "score_breakdown": {{
        "savings": <0-100>,
        "debt_management": <0-100>,
        "goal_progress": <0-100>,
        "spending_habits": <0-100>,
        "emergency_fund": <0-100>
    }},
    "summary": "<one paragraph summary>",
    "top_strengths": ["strength1", "strength2"],
    "areas_to_improve": ["area1", "area2"],
    "personalized_tips": ["tip1", "tip2", "tip3"]
}}"""
        
        return await self.generate_json(prompt, system_prompt)


# Singleton instance
groq_client = GroqClient()

