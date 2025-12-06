"""
SQLAlchemy base model with common fields.

Provides base classes for all database models.
"""

from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    Provides automatic table naming based on class name.
    """
    
    id: Any
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.
        
        Converts CamelCase to snake_case and adds 's' for plural.
        Example: UserProfile -> user_profiles
        """
        name = cls.__name__
        # Convert CamelCase to snake_case
        import re
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        # Add 's' for plural if not already ending in 's'
        if not snake_case.endswith('s'):
            snake_case += 's'
        return snake_case


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps.
    
    These fields are automatically managed:
    - created_at: Set on insert
    - updated_at: Set on insert and updated on every update
    """
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when the record was last updated"
    )


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model with id and timestamp fields.
    
    All models should inherit from this class to get:
    - Auto-incrementing integer id
    - created_at timestamp
    - updated_at timestamp
    """
    
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Primary key"
    )
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

