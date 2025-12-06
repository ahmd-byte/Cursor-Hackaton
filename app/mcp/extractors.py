"""
Financial data extractors for MCP tools.

Provides extraction logic for various financial document types.
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal


class FinancialExtractor:
    """
    Extraction utilities for financial data.
    
    Provides methods for parsing and extracting structured
    financial information from various formats.
    """
    
    @staticmethod
    def extract_amounts(text: str) -> List[Dict[str, Any]]:
        """
        Extract monetary amounts from text.
        
        Args:
            text: Text to extract amounts from
            
        Returns:
            List of extracted amounts with context
        """
        amounts = []
        
        # Patterns for various currency formats
        patterns = [
            r'\$[\d,]+\.?\d*',  # $1,234.56
            r'USD[\s]?[\d,]+\.?\d*',  # USD 1234.56
            r'[\d,]+\.?\d*[\s]?(?:dollars|USD)',  # 1234.56 dollars
            r'(?:Rp|IDR)[\s]?[\d.,]+',  # Rp 1.234.567 or IDR
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group()
                # Extract numeric value
                numeric = re.sub(r'[^\d.]', '', amount_str.replace(',', ''))
                try:
                    value = float(numeric)
                    amounts.append({
                        "raw": amount_str,
                        "value": value,
                        "position": match.start(),
                        "context": text[max(0, match.start()-20):match.end()+20]
                    })
                except ValueError:
                    continue
        
        return amounts
    
    @staticmethod
    def extract_dates(text: str) -> List[Dict[str, Any]]:
        """
        Extract dates from text.
        
        Args:
            text: Text to extract dates from
            
        Returns:
            List of extracted dates
        """
        dates = []
        
        # Date patterns
        patterns = [
            (r'\d{1,2}/\d{1,2}/\d{2,4}', '%m/%d/%Y'),  # MM/DD/YYYY
            (r'\d{1,2}-\d{1,2}-\d{2,4}', '%m-%d-%Y'),  # MM-DD-YYYY
            (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'),  # YYYY-MM-DD
            (r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{1,2}[\s,]+\d{4}', None),
        ]
        
        for pattern, date_format in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                try:
                    if date_format:
                        # Adjust for 2-digit year
                        if len(date_str.split('/')[-1]) == 2 or len(date_str.split('-')[-1]) == 2:
                            date_format = date_format.replace('%Y', '%y')
                        parsed = datetime.strptime(date_str, date_format)
                    else:
                        # Use dateutil for complex formats
                        from dateutil import parser
                        parsed = parser.parse(date_str)
                    
                    dates.append({
                        "raw": date_str,
                        "parsed": parsed.isoformat(),
                        "position": match.start()
                    })
                except (ValueError, ImportError):
                    continue
        
        return dates
    
    @staticmethod
    def extract_account_numbers(text: str) -> List[Dict[str, Any]]:
        """
        Extract account numbers from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            List of potential account numbers (masked)
        """
        accounts = []
        
        # Patterns for account numbers
        patterns = [
            r'(?:account|acct|a/c)[\s#:]*(\d{4,})',
            r'(?:card|cc)[\s#:]*(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})',
            r'(?:routing)[\s#:]*(\d{9})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                number = match.group(1)
                # Mask the number for security
                masked = '*' * (len(number) - 4) + number[-4:]
                accounts.append({
                    "type": "account" if "account" in pattern else "card" if "card" in pattern else "routing",
                    "masked": masked,
                    "last_four": number[-4:]
                })
        
        return accounts
    
    @staticmethod
    def extract_transactions(text: str) -> List[Dict[str, Any]]:
        """
        Extract transaction-like entries from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            List of potential transactions
        """
        transactions = []
        
        # Look for lines that appear to be transactions
        lines = text.split('\n')
        
        for line in lines:
            # Skip empty or header-like lines
            if len(line.strip()) < 10:
                continue
            
            # Extract amounts from line
            amounts = FinancialExtractor.extract_amounts(line)
            dates = FinancialExtractor.extract_dates(line)
            
            if amounts:
                transaction = {
                    "line": line.strip(),
                    "amounts": amounts,
                    "dates": dates,
                    "type": "credit" if any(
                        word in line.lower() 
                        for word in ["deposit", "credit", "received", "payment from"]
                    ) else "debit" if any(
                        word in line.lower() 
                        for word in ["withdrawal", "debit", "payment", "purchase", "fee"]
                    ) else "unknown"
                }
                transactions.append(transaction)
        
        return transactions
    
    @staticmethod
    def categorize_description(description: str) -> Dict[str, Any]:
        """
        Categorize a transaction description.
        
        Args:
            description: Transaction description
            
        Returns:
            Category information
        """
        description_lower = description.lower()
        
        # Category keywords
        categories = {
            "groceries": ["grocery", "supermarket", "food", "walmart", "costco", "trader joe"],
            "dining": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "uber eats", "doordash"],
            "transportation": ["gas", "fuel", "uber", "lyft", "taxi", "parking", "transit"],
            "utilities": ["electric", "water", "gas bill", "internet", "phone", "utility"],
            "entertainment": ["netflix", "spotify", "movie", "theater", "game", "steam"],
            "shopping": ["amazon", "target", "best buy", "clothing", "store"],
            "healthcare": ["pharmacy", "doctor", "hospital", "medical", "dental", "health"],
            "income": ["salary", "payroll", "deposit", "direct dep", "payment received"],
            "transfer": ["transfer", "zelle", "venmo", "paypal"],
        }
        
        for category, keywords in categories.items():
            if any(kw in description_lower for kw in keywords):
                return {
                    "category": category,
                    "confidence": 0.8,
                    "matched_keyword": next(
                        kw for kw in keywords if kw in description_lower
                    )
                }
        
        return {
            "category": "other",
            "confidence": 0.5,
            "matched_keyword": None
        }
    
    @staticmethod
    def parse_bank_statement_text(text: str) -> Dict[str, Any]:
        """
        Parse a bank statement from extracted text.
        
        Args:
            text: Bank statement text
            
        Returns:
            Structured bank statement data
        """
        result = {
            "transactions": [],
            "opening_balance": None,
            "closing_balance": None,
            "total_deposits": Decimal("0"),
            "total_withdrawals": Decimal("0"),
            "dates_found": [],
            "accounts_found": []
        }
        
        # Extract components
        result["dates_found"] = FinancialExtractor.extract_dates(text)
        result["accounts_found"] = FinancialExtractor.extract_account_numbers(text)
        
        # Look for balance information
        balance_patterns = [
            (r'(?:opening|beginning|start)[\s]+balance[:\s]*\$?([\d,]+\.?\d*)', 'opening'),
            (r'(?:closing|ending|final)[\s]+balance[:\s]*\$?([\d,]+\.?\d*)', 'closing'),
        ]
        
        for pattern, balance_type in balance_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = Decimal(match.group(1).replace(',', ''))
                    result[f"{balance_type}_balance"] = float(value)
                except (ValueError, InvalidOperation):
                    pass
        
        # Extract transactions
        transactions = FinancialExtractor.extract_transactions(text)
        for txn in transactions:
            if txn["amounts"]:
                amount = txn["amounts"][0]["value"]
                if txn["type"] == "credit":
                    result["total_deposits"] += Decimal(str(amount))
                elif txn["type"] == "debit":
                    result["total_withdrawals"] += Decimal(str(amount))
                
                result["transactions"].append({
                    "description": txn["line"][:100],
                    "amount": amount,
                    "type": txn["type"],
                    "date": txn["dates"][0]["parsed"] if txn["dates"] else None
                })
        
        result["total_deposits"] = float(result["total_deposits"])
        result["total_withdrawals"] = float(result["total_withdrawals"])
        
        return result


# For backwards compatibility
from decimal import InvalidOperation

