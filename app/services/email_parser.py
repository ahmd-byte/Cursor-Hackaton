"""
Email parser service for extracting financial data from emails.

Integrates with Gmail API to fetch and parse financial emails.
"""

import json
import base64
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.ai.gemini_client import gemini_client
from app.mcp.extractors import FinancialExtractor
from app.models.financial_data import FinancialData, DataSource, ProcessingStatus


class EmailParser:
    """
    Email parser for extracting financial data from emails.
    
    Supports Gmail API integration for fetching emails
    and AI-powered extraction of financial information.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize email parser."""
        self.db = db
        self.gemini = gemini_client
        self.extractor = FinancialExtractor()
        self._gmail_service = None
    
    async def initialize_gmail(self, credentials_path: Optional[str] = None) -> bool:
        """
        Initialize Gmail API service.
        
        Args:
            credentials_path: Path to OAuth credentials
            
        Returns:
            True if initialization successful
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import os
            import pickle
            
            creds = None
            token_path = settings.gmail_token_path or "token.pickle"
            creds_path = credentials_path or settings.gmail_credentials_path
            
            # Load existing token
            if os.path.exists(token_path):
                with open(token_path, "rb") as token:
                    creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif creds_path and os.path.exists(creds_path):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        creds_path,
                        scopes=[settings.email_scopes]
                    )
                    creds = flow.run_local_server(port=0)
                else:
                    return False
                
                # Save credentials
                with open(token_path, "wb") as token:
                    pickle.dump(creds, token)
            
            self._gmail_service = build("gmail", "v1", credentials=creds)
            return True
            
        except Exception:
            return False
    
    async def fetch_financial_emails(
        self,
        user_id: int,
        days: int = 30,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch financial emails from Gmail.
        
        Args:
            user_id: User ID for storing results
            days: Number of days to look back
            max_results: Maximum emails to fetch
            
        Returns:
            List of parsed email data
        """
        if not self._gmail_service:
            # Return mock data if Gmail not initialized
            return await self._get_mock_emails()
        
        try:
            # Build search query for financial emails
            query_parts = [
                "from:(bank OR payroll OR payment)",
                "subject:(statement OR transaction OR salary OR payment OR receipt)",
                f"after:{(datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')}"
            ]
            query = " OR ".join(query_parts)
            
            # Fetch emails
            results = self._gmail_service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get("messages", [])
            parsed_emails = []
            
            for msg in messages:
                email_data = await self._parse_email(msg["id"], user_id)
                if email_data:
                    parsed_emails.append(email_data)
            
            return parsed_emails
            
        except Exception as e:
            return []
    
    async def _parse_email(
        self,
        message_id: str,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Parse a single email and extract financial data."""
        try:
            message = self._gmail_service.users().messages().get(
                userId="me",
                id=message_id,
                format="full"
            ).execute()
            
            # Extract headers
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
            
            # Extract body
            body = self._extract_email_body(message["payload"])
            
            # Parse financial data
            financial_data = await self._extract_financial_info(
                subject=headers.get("Subject", ""),
                sender=headers.get("From", ""),
                body=body,
                date=headers.get("Date", "")
            )
            
            # Store in database
            if financial_data:
                record = FinancialData(
                    user_id=user_id,
                    source=DataSource.EMAIL_TRANSACTION,
                    source_identifier=message_id,
                    data_json=json.dumps(financial_data),
                    processing_status=ProcessingStatus.COMPLETED,
                    confidence_score=financial_data.get("confidence_score", 70),
                    extraction_method="email_parser"
                )
                self.db.add(record)
                await self.db.commit()
            
            return {
                "message_id": message_id,
                "subject": headers.get("Subject", ""),
                "sender": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "financial_data": financial_data
            }
            
        except Exception:
            return None
    
    def _extract_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract text body from email payload."""
        body = ""
        
        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
        elif "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if part["body"].get("data"):
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                        break
        
        return body
    
    async def _extract_financial_info(
        self,
        subject: str,
        sender: str,
        body: str,
        date: str
    ) -> Dict[str, Any]:
        """Extract financial information from email content."""
        # Identify email type
        email_type = self._identify_email_type(subject, sender)
        
        # Extract using pattern matching
        amounts = self.extractor.extract_amounts(body)
        dates = self.extractor.extract_dates(body)
        accounts = self.extractor.extract_account_numbers(body)
        
        result = {
            "email_type": email_type,
            "subject": subject,
            "sender": sender,
            "date": date,
            "amounts": amounts,
            "dates_found": dates,
            "accounts": accounts,
            "confidence_score": 70
        }
        
        # Enhance with AI for complex emails
        if email_type in ["bank_statement", "transaction_alert"] and body:
            try:
                ai_extraction = await self.gemini.generate_json(
                    f"""Extract financial information from this {email_type} email:

Subject: {subject}
From: {sender}

Content:
{body[:2000]}

Return JSON with:
- transaction_type (credit/debit/info)
- amount (if present)
- description
- account_info (masked)
- date
- merchant (if applicable)
"""
                )
                result["ai_extraction"] = ai_extraction
                result["confidence_score"] = 85
            except Exception:
                pass
        
        return result
    
    def _identify_email_type(self, subject: str, sender: str) -> str:
        """Identify the type of financial email."""
        subject_lower = subject.lower()
        sender_lower = sender.lower()
        
        # Transaction alerts
        if any(word in subject_lower for word in ["transaction", "alert", "notification", "purchase"]):
            return "transaction_alert"
        
        # Statements
        if any(word in subject_lower for word in ["statement", "summary", "monthly"]):
            return "bank_statement"
        
        # Salary/payroll
        if any(word in subject_lower for word in ["salary", "payroll", "payslip", "pay stub"]):
            return "salary_notification"
        
        # Payment confirmations
        if any(word in subject_lower for word in ["payment", "receipt", "confirmation", "invoice"]):
            return "payment_confirmation"
        
        # Bank notifications
        if any(word in sender_lower for word in ["bank", "finance", "credit"]):
            return "bank_notification"
        
        return "general"
    
    async def _get_mock_emails(self) -> List[Dict[str, Any]]:
        """Return mock email data for testing."""
        return [
            {
                "message_id": "mock_1",
                "subject": "Your account statement is ready",
                "sender": "noreply@bank.com",
                "date": datetime.now().isoformat(),
                "financial_data": {
                    "email_type": "bank_statement",
                    "amounts": [{"value": 5000.00, "raw": "$5,000.00"}],
                    "confidence_score": 80
                }
            },
            {
                "message_id": "mock_2",
                "subject": "Salary Credit Notification",
                "sender": "payroll@company.com",
                "date": datetime.now().isoformat(),
                "financial_data": {
                    "email_type": "salary_notification",
                    "amounts": [{"value": 8500.00, "raw": "$8,500.00"}],
                    "confidence_score": 90
                }
            },
            {
                "message_id": "mock_3",
                "subject": "Transaction Alert - Debit",
                "sender": "alerts@bank.com",
                "date": datetime.now().isoformat(),
                "financial_data": {
                    "email_type": "transaction_alert",
                    "amounts": [{"value": 125.50, "raw": "$125.50"}],
                    "transaction_type": "debit",
                    "confidence_score": 85
                }
            }
        ]
    
    async def sync_financial_emails(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Synchronize financial emails for a user.
        
        Args:
            user_id: User ID
            days: Days to look back
            
        Returns:
            Sync summary
        """
        emails = await self.fetch_financial_emails(user_id, days)
        
        processed = 0
        total_amount = 0.0
        
        for email in emails:
            if email.get("financial_data"):
                processed += 1
                amounts = email["financial_data"].get("amounts", [])
                for amt in amounts:
                    total_amount += amt.get("value", 0)
        
        return {
            "success": True,
            "emails_found": len(emails),
            "emails_processed": processed,
            "total_financial_amount": total_amount,
            "sync_date": datetime.utcnow().isoformat()
        }

