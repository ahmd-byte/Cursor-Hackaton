"""
Configuration management using Pydantic Settings.

Loads environment variables and provides type-safe configuration access.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ===========================================
    # Application Configuration
    # ===========================================
    app_name: str = "financial_ai_app"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-this-secret-key-in-production-min-32-chars"
    api_version: str = "v1"
    
    # ===========================================
    # Database Configuration (TiDB)
    # ===========================================
    tidb_host: str = "localhost"
    tidb_port: int = 4000
    tidb_user: str = "root"
    tidb_password: str = ""
    tidb_database: str = "finapp"
    tidb_ssl_ca: Optional[str] = None
    
    # Connection pool settings
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_recycle: int = 3600
    db_echo: bool = False
    
    @property
    def database_url(self) -> str:
        """Construct the async database URL for TiDB."""
        base_url = f"mysql+asyncmy://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_database}"
        if self.tidb_ssl_ca:
            return f"{base_url}?ssl_ca={self.tidb_ssl_ca}"
        return base_url
    
    @property
    def sync_database_url(self) -> str:
        """Construct the sync database URL for Alembic migrations."""
        base_url = f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_database}"
        if self.tidb_ssl_ca:
            return f"{base_url}?ssl_ca={self.tidb_ssl_ca}"
        return base_url
    
    # ===========================================
    # AI/ML Configuration
    # ===========================================
    
    # Groq API (Fast Inference)
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"
    groq_max_tokens: int = 4096
    groq_temperature: float = 0.2
    
    # Gemini API (Document Understanding)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    gemini_vision_model: str = "gemini-1.5-pro"
    gemini_max_tokens: int = 8192
    gemini_temperature: float = 0.2
    
    # ===========================================
    # MCP Configuration
    # ===========================================
    mcp_server_url: str = "http://localhost:8001"
    mcp_api_key: str = ""
    mcp_timeout: int = 30
    enable_mcp: bool = True
    
    # ===========================================
    # Email Integration
    # ===========================================
    email_provider: str = "gmail"
    gmail_credentials_path: Optional[str] = None
    gmail_token_path: Optional[str] = None
    email_oauth_client_id: Optional[str] = None
    email_oauth_client_secret: Optional[str] = None
    email_scopes: str = "https://www.googleapis.com/auth/gmail.readonly"
    
    # ===========================================
    # Google Cloud Platform
    # ===========================================
    gcp_project_id: Optional[str] = None
    gcp_region: str = "us-central1"
    gcp_credentials_path: Optional[str] = None
    gcs_bucket_name: Optional[str] = None
    gcs_documents_path: str = "documents/"
    gcs_temp_path: str = "temp/"
    
    # ===========================================
    # Security & Authentication
    # ===========================================
    jwt_secret_key: str = "change-this-jwt-secret-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12
    
    # ===========================================
    # Rate Limiting
    # ===========================================
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # ===========================================
    # Logging
    # ===========================================
    log_level: str = "INFO"
    log_format: str = "json"
    
    # ===========================================
    # Feature Flags
    # ===========================================
    enable_ai_allocation: bool = True
    enable_email_extraction: bool = True
    enable_auto_allocation: bool = True
    enable_document_upload: bool = True
    
    # ===========================================
    # Wage Access Settings
    # ===========================================
    max_wage_advance_percent: float = 50.0
    min_days_worked: int = 1
    advance_fee_percent: float = 2.5


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()

