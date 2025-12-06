"""
Gemini API client for multimodal AI capabilities.

Provides wrapper for Google's Gemini API for document understanding
and image processing.
"""

import json
import base64
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings


class GeminiClient:
    """
    Client for Google Gemini API interactions.
    
    Gemini excels at multimodal tasks like document understanding,
    image analysis, and extracting structured data from various formats.
    """
    
    def __init__(self):
        """Initialize Gemini client with API key from settings."""
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.vision_model_name = settings.gemini_vision_model
        self.max_tokens = settings.gemini_max_tokens
        self.temperature = settings.gemini_temperature
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self._text_model = None
        self._vision_model = None
    
    @property
    def text_model(self):
        """Get or create text generation model."""
        if self._text_model is None:
            self._text_model = genai.GenerativeModel(self.model_name)
        return self._text_model
    
    @property
    def vision_model(self):
        """Get or create vision model."""
        if self._vision_model is None:
            self._vision_model = genai.GenerativeModel(self.vision_model_name)
        return self._vision_model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text response
        """
        generation_config = genai.GenerationConfig(
            temperature=temperature or self.temperature,
            max_output_tokens=max_tokens or self.max_tokens
        )
        
        model = self.text_model
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
        
        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    async def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            
        Returns:
            Parsed JSON dictionary
        """
        full_instruction = (system_instruction or "") + "\n\nRespond only with valid JSON."
        
        response = await self.generate(
            prompt=prompt,
            system_instruction=full_instruction
        )
        
        # Clean response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return json.loads(response.strip())
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def analyze_image(
        self,
        image_data: Union[bytes, str, Path],
        prompt: str,
        mime_type: str = "image/jpeg"
    ) -> str:
        """
        Analyze an image using Gemini Vision.
        
        Args:
            image_data: Image bytes, base64 string, or file path
            prompt: Analysis prompt
            mime_type: MIME type of the image
            
        Returns:
            Analysis result
        """
        # Handle different input types
        if isinstance(image_data, Path):
            with open(image_data, "rb") as f:
                image_bytes = f.read()
        elif isinstance(image_data, str):
            if image_data.startswith("data:"):
                # Data URL
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        
        # Create image part
        image_part = {
            "mime_type": mime_type,
            "data": base64.b64encode(image_bytes).decode()
        }
        
        response = await self.vision_model.generate_content_async(
            [prompt, image_part]
        )
        
        return response.text
    
    async def extract_financial_data_from_image(
        self,
        image_data: Union[bytes, str, Path],
        document_type: str = "bank_statement",
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Extract financial data from a document image.
        
        Args:
            image_data: Image bytes, base64 string, or file path
            document_type: Type of document (bank_statement, pay_stub, receipt, etc.)
            mime_type: MIME type of the image
            
        Returns:
            Extracted financial data as dictionary
        """
        extraction_prompts = {
            "bank_statement": """Extract all financial information from this bank statement image.
Include:
- Account holder name
- Account number (last 4 digits only)
- Statement period
- Opening balance
- Closing balance
- All transactions with dates, descriptions, and amounts
- Total deposits
- Total withdrawals

Return as JSON with this structure:
{
    "account_holder": "name",
    "account_number_last4": "XXXX",
    "statement_period": {"start": "date", "end": "date"},
    "opening_balance": number,
    "closing_balance": number,
    "transactions": [{"date": "date", "description": "desc", "amount": number, "type": "credit|debit"}],
    "total_deposits": number,
    "total_withdrawals": number,
    "confidence_score": 0-100
}""",
            
            "pay_stub": """Extract all information from this pay stub/salary slip image.
Include:
- Employee name
- Employer name
- Pay period
- Gross pay
- Net pay
- All deductions with amounts
- Any bonuses or additions

Return as JSON with this structure:
{
    "employee_name": "name",
    "employer_name": "name",
    "pay_period": {"start": "date", "end": "date"},
    "gross_pay": number,
    "net_pay": number,
    "deductions": [{"name": "deduction name", "amount": number}],
    "additions": [{"name": "addition name", "amount": number}],
    "confidence_score": 0-100
}""",
            
            "receipt": """Extract information from this receipt/invoice image.
Include:
- Merchant/store name
- Date
- All items with prices
- Subtotal
- Tax
- Total
- Payment method if visible

Return as JSON with this structure:
{
    "merchant": "name",
    "date": "date",
    "items": [{"name": "item", "quantity": number, "price": number}],
    "subtotal": number,
    "tax": number,
    "total": number,
    "payment_method": "method or null",
    "confidence_score": 0-100
}"""
        }
        
        prompt = extraction_prompts.get(
            document_type,
            "Extract all financial information from this document image. Return as structured JSON."
        )
        
        response = await self.analyze_image(image_data, prompt, mime_type)
        
        # Parse JSON from response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return json.loads(response.strip())
    
    async def extract_text_from_document(
        self,
        document_data: Union[bytes, str, Path],
        mime_type: str = "application/pdf"
    ) -> str:
        """
        Extract text content from a document.
        
        Args:
            document_data: Document bytes, base64 string, or file path
            mime_type: MIME type of the document
            
        Returns:
            Extracted text content
        """
        prompt = """Extract all text content from this document.
Maintain the structure and formatting as much as possible.
Include all visible text, numbers, and data."""
        
        return await self.analyze_image(document_data, prompt, mime_type)
    
    async def categorize_transaction(
        self,
        description: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description
            amount: Transaction amount
            
        Returns:
            Category information
        """
        prompt = f"""Categorize this financial transaction:

Description: {description}
Amount: ${amount:.2f}

Return JSON with:
{{
    "category": "one of: groceries, dining, transportation, utilities, entertainment, shopping, healthcare, education, income, transfer, other",
    "subcategory": "more specific category",
    "merchant_type": "type of merchant/business",
    "is_recurring": true/false,
    "confidence": 0-100
}}"""
        
        return await self.generate_json(prompt)
    
    async def summarize_financial_document(
        self,
        document_text: str,
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate a summary of a financial document.
        
        Args:
            document_text: Extracted text from document
            document_type: Type of document
            
        Returns:
            Summary with key points
        """
        prompt = f"""Summarize this {document_type} financial document:

{document_text}

Return JSON with:
{{
    "summary": "2-3 sentence summary",
    "key_figures": {{"figure_name": value}},
    "important_dates": ["date1", "date2"],
    "action_items": ["item1", "item2"],
    "warnings": ["any concerns or issues"]
}}"""
        
        return await self.generate_json(prompt)


# Singleton instance
gemini_client = GeminiClient()

