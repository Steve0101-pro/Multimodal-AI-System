from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AliasChoices, Field, SecretStr, field_validator
import os
from pathlib import Path
from typing import Literal

BASE_DIR = Path(__file__).resolve().parent.parent

class AppSettings(BaseSettings):
    """Application configuration with validation."""
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database
    DATABASE_URL: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://user:password@localhost:5432/document_intelligence"),
        description="PostgreSQL database URL"
    )
    
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )

    CORS_ORIGINS: str = Field(
        default="http://localhost:8501",
        description="Comma-separated browser origins allowed to call the API",
    )
    
    # API Keys and URLs
    OPENAI_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="OpenAI API key"
    )
    OPENAI_FALLBACK_MODEL: str = Field(
        default="gpt-4-turbo",
        description="OpenAI fallback model"
    )
    
    NVIDIA_API_KEY: SecretStr = Field(
        description="NVIDIA API key"
    )
    NVIDIA_BASE_URL: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        description="NVIDIA API base URL"
    )
    NVIDIA_PRIMARY_MODEL: str = Field(
        default="meta/llama-3.2-90b-vision-instruct",
        description="NVIDIA primary model"
    )
    
    GROQ_API_KEY: SecretStr = Field(
        description="Groq API key"
    )
    GROQ_MODEL: str = Field(
        default="mixtral-8x7b-32768",
        description="Groq model"
    )
    
    GEMINI_API_KEY: SecretStr = Field(
        description="Google Gemini API key"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.0-flash",
        description="Google Gemini model"
    )
    GEMINI_TTS_MODEL: str = Field(
        default="gemini-2.0-flash",
        description="Google Gemini TTS model"
    )
    
    # Supabase
    SUPABASE_SERVICE_KEY: SecretStr = Field(
        description="Supabase service key"
    )
    SUPABASE_URL: str = Field(
        description="Supabase project URL"
    )
    SUPABASE_BUCKET_NAME: str = Field(
        default="documents",
        description="Supabase storage bucket name"
    )
    
    # Redis
    REDIS_URL: SecretStr = Field(
        default=SecretStr("redis://localhost:6379/0"),
        description="Redis URL"
    )
    
    # JWT
    JWT_SECRET_KEY: SecretStr = Field(
        description="JWT secret key for token signing"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Access token expiration time in minutes"
    )
    SMTP_HOST: str = Field(default="", description="SMTP server hostname")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: SecretStr = Field(default=SecretStr(""), description="SMTP password")
    SMTP_FROM_EMAIL: str = Field(default="", description="Password recovery sender")
    PASSWORD_RESET_EXPIRE_MINUTES: int = Field(default=30, gt=0)

    # Portkeys
    PORTKEYS_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Portkeys API key for LLM monitoring and routing"
    )
    PORTKEYS_ENABLED: bool = Field(
        default=False,
        description="Enable Portkeys integration for LLM monitoring"
    )
    PORTKEYS_VIRTUAL_KEY: str = Field(
        default="",
        description="Portkey saved integration slug, for example @nvidia-production",
    )

    # LangSmith tracing
    LANGCHAIN_TRACING_V2: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "LANGSMITH_TRACING",
            "LANGSMITH_TRACING_V2",
            "LANGCHAIN_TRACING_V2",
        ),
        description="Enable LangSmith tracing"
    )
    LANGCHAIN_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("LANGSMITH_API_KEY", "LANGCHAIN_API_KEY"),
        description="LangSmith API key"
    )
    LANGCHAIN_PROJECT: str = Field(
        default="document-intelligence",
        validation_alias=AliasChoices("LANGSMITH_PROJECT", "LANGCHAIN_PROJECT"),
        description="LangSmith project name"
    )
    LANGCHAIN_ENDPOINT: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith API endpoint"
    )
    PROMPT_VERSION: str = Field(default="v1", max_length=80)
    AB_TEST_ENABLED: bool = Field(default=False)
    AB_TEST_VARIANTS: str = Field(default="control")
    ONLINE_EVAL_ENABLED: bool = Field(default=False)
    ONLINE_EVAL_SAMPLE_RATE: float = Field(default=1.0, ge=0.0, le=1.0)
    RETENTION_DAYS: int = Field(default=90, gt=0)
    
    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def validate_token_expire_minutes(cls, v: int) -> int:
        """Validate that token expiration is positive."""
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        return v
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    @property
    def debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.ENVIRONMENT == "development"


def initialize_settings() -> AppSettings:
    """Initialize and validate application settings."""
    config = AppSettings()
    os.environ["DATABASE_URL"] = config.DATABASE_URL.get_secret_value()
    os.environ["LANGCHAIN_TRACING_V2"] = str(config.LANGCHAIN_TRACING_V2).lower()
    os.environ["LANGCHAIN_PROJECT"] = config.LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = config.LANGCHAIN_ENDPOINT
    os.environ["LANGSMITH_TRACING"] = str(config.LANGCHAIN_TRACING_V2).lower()
    os.environ["LANGSMITH_PROJECT"] = config.LANGCHAIN_PROJECT
    os.environ["LANGSMITH_ENDPOINT"] = config.LANGCHAIN_ENDPOINT

    langchain_api_key = config.LANGCHAIN_API_KEY.get_secret_value()
    if langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
        os.environ["LANGSMITH_API_KEY"] = langchain_api_key
    return config


# Execute the helper function instead of direct instantiation
settings = initialize_settings()
