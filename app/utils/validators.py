"""
Input validation utilities.

Provides validation functions for common input types.
"""

import re
from decimal import Decimal
from typing import Optional
from email_validator import validate_email as validate_email_format, EmailNotValidError


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate an email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, normalized_email or error_message)
    """
    try:
        # Validate and get normalized email
        validation = validate_email_format(email, check_deliverability=False)
        return True, validation.email
    except EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength requirements.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def validate_amount(
    amount: Decimal,
    min_amount: Decimal = Decimal("0.01"),
    max_amount: Decimal = Decimal("999999999.99")
) -> tuple[bool, Optional[str]]:
    """
    Validate a monetary amount.
    
    Args:
        amount: Amount to validate
        min_amount: Minimum allowed amount
        max_amount: Maximum allowed amount
        
    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if amount < min_amount:
        return False, f"Amount must be at least {min_amount}"
    
    if amount > max_amount:
        return False, f"Amount cannot exceed {max_amount}"
    
    # Check decimal places (max 2)
    if amount.as_tuple().exponent < -2:
        return False, "Amount can have at most 2 decimal places"
    
    return True, None


def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
    """
    Validate a phone number format.
    
    Accepts formats like:
    - +1234567890
    - 1234567890
    - +1 234 567 890
    - 123-456-7890
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, normalized_phone or error_message)
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    
    # Check if it matches a valid pattern
    pattern = r"^\+?\d{10,15}$"
    if re.match(pattern, cleaned):
        return True, cleaned
    
    return False, "Invalid phone number format"


def validate_priority(priority: int) -> tuple[bool, Optional[str]]:
    """
    Validate a priority value (1-10).
    
    Args:
        priority: Priority value to validate
        
    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if priority < 1 or priority > 10:
        return False, "Priority must be between 1 and 10"
    return True, None


def validate_risk_tolerance(risk_tolerance: int) -> tuple[bool, Optional[str]]:
    """
    Validate a risk tolerance value (1-10).
    
    Args:
        risk_tolerance: Risk tolerance value to validate
        
    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if risk_tolerance < 1 or risk_tolerance > 10:
        return False, "Risk tolerance must be between 1 and 10"
    return True, None


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize a string input.
    
    - Strips whitespace
    - Limits length
    - Removes control characters
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    # Strip whitespace
    value = value.strip()
    
    # Remove control characters
    value = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", value)
    
    # Limit length
    return value[:max_length]

