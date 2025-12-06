"""
User model for authentication and profile management.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Numeric,
    Integer,
    Text,
    Index,
)
from sqlalchemy.orm import relationship, Mapped

from app.database.base import BaseModel

if TYPE_CHECKING:
    from app.models.bucket import Bucket
    from app.models.transaction import Transaction
    from app.models.financial_data import FinancialData


class User(BaseModel):
    """
    User model representing application users.
    
    Attributes:
        email: Unique email address for authentication
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        employer_id: Reference to employer for payroll integration
        daily_rate: Daily wage rate for early access calculations
        monthly_salary: Monthly salary for AI allocation
        is_active: Whether the user account is active
        is_verified: Whether email is verified
        risk_tolerance: User's risk tolerance level (1-10)
        financial_goals: JSON string of user's financial goals
    """
    
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User's email address"
    )
    hashed_password = Column(
        String(255),
        nullable=False,
        doc="Bcrypt hashed password"
    )
    
    # Profile fields
    full_name = Column(
        String(255),
        nullable=False,
        doc="User's full name"
    )
    phone_number = Column(
        String(20),
        nullable=True,
        doc="User's phone number"
    )
    
    # Employment fields
    employer_id = Column(
        String(100),
        nullable=True,
        index=True,
        doc="Employer identifier for payroll integration"
    )
    employee_id = Column(
        String(100),
        nullable=True,
        doc="Employee ID within the employer's system"
    )
    daily_rate = Column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
        doc="Daily wage rate for early access calculations"
    )
    monthly_salary = Column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
        doc="Monthly salary amount"
    )
    pay_cycle_day = Column(
        Integer,
        default=25,
        nullable=False,
        doc="Day of month when salary is paid (1-31)"
    )
    
    # Account status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active"
    )
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user's email is verified"
    )
    
    # Tiered savings configuration
    current_savings_tier = Column(
        Integer,
        default=1,
        nullable=False,
        doc="Current savings tier: 1=20%, 2=15%, 3+=5%"
    )
    
    # Financial profile for AI allocation
    risk_tolerance = Column(
        Integer,
        default=5,
        nullable=False,
        doc="Risk tolerance level from 1 (conservative) to 10 (aggressive)"
    )
    financial_goals = Column(
        Text,
        nullable=True,
        doc="JSON string of user's financial goals and priorities"
    )
    
    # Relationships
    buckets: Mapped[List["Bucket"]] = relationship(
        "Bucket",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    financial_data: Mapped[List["FinancialData"]] = relationship(
        "FinancialData",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_users_employer_employee", "employer_id", "employee_id"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
    
    @property
    def available_wage_advance(self) -> Decimal:
        """
        Calculate available wage advance based on days worked.
        
        This is a simplified calculation. Actual implementation
        should integrate with payroll system.
        """
        from datetime import datetime
        
        # Get current day of month
        today = datetime.now()
        days_worked = today.day
        
        # Calculate earned wages
        earned = self.daily_rate * days_worked
        
        # Return 50% of earned wages (configurable)
        from app.config import settings
        max_percent = Decimal(str(settings.max_wage_advance_percent)) / Decimal("100")
        return earned * max_percent

