"""
Configuration management for Proxmox AI Assistant.

Handles application settings, environment configuration, and security settings
using Pydantic for validation and type safety.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import structlog

logger = structlog.get_logger(__name__)


class ProxmoxConfig(BaseModel):
    """Proxmox VE server configuration."""
    
    host: str = Field(..., description="Proxmox VE host address")
    port: int = Field(8006, description="Proxmox VE API port", ge=1, le=65535)
    user: str = Field("root@pam", description="Proxmox VE username")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    timeout: int = Field(30, description="API request timeout in seconds", ge=1)
    
    @validator('host')
    def validate_host(cls, v):
        """Validate host format."""
        if not v or v.isspace():
            raise ValueError("Host cannot be empty")
        # Remove protocol if provided
        if v.startswith(('http://', 'https://')):
            v = v.split('://', 1)[1]
        return v.strip()


class LocalAIConfig(BaseModel):
    """Local AI model configuration."""
    
    model_name: str = Field("llama3.2", description="Local AI model name")
    ollama_host: str = Field("http://localhost:11434", description="Ollama host URL")
    max_tokens: int = Field(2048, description="Maximum tokens per request", ge=1)
    temperature: float = Field(0.1, description="Model temperature", ge=0.0, le=2.0)
    timeout: int = Field(60, description="AI request timeout in seconds", ge=1)
    skill_level: str = Field("intermediate", description="Default skill level (beginner/intermediate/expert)")


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    
    enable_audit_logging: bool = Field(True, description="Enable security audit logging")
    log_sensitive_data: bool = Field(False, description="Log sensitive data (NOT recommended)")
    session_timeout: int = Field(3600, description="Session timeout in seconds", ge=60)
    max_retry_attempts: int = Field(3, description="Maximum retry attempts", ge=1, le=10)
    credential_cache_ttl: int = Field(900, description="Credential cache TTL in seconds", ge=60)


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    
    level: str = Field("INFO", description="Log level")
    format: str = Field("json", description="Log format (json or console)")
    file_path: Optional[Path] = Field(None, description="Log file path")
    max_file_size: int = Field(10485760, description="Max log file size in bytes", ge=1024)
    backup_count: int = Field(5, description="Number of backup log files", ge=1)
    
    @validator('level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator('format')
    def validate_log_format(cls, v):
        """Validate log format."""
        valid_formats = {'json', 'console'}
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of: {valid_formats}")
        return v.lower()


class Settings(BaseSettings):
    """
    Main application settings.
    
    Loads configuration from environment variables, .env files, and provides
    sensible defaults for all settings.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application settings
    app_name: str = Field("Proxmox AI Assistant", description="Application name")
    version: str = Field("0.1.0", description="Application version")
    debug: bool = Field(False, description="Enable debug mode")
    enable_ai_generation: bool = Field(True, description="Enable AI generation features")
    
    # Configuration file paths
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".config" / "proxmox-ai",
        description="Configuration directory"
    )
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".local" / "share" / "proxmox-ai",
        description="Data directory"
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".cache" / "proxmox-ai",
        description="Cache directory"
    )
    
    # Component configurations
    proxmox: ProxmoxConfig = Field(
        default_factory=lambda: ProxmoxConfig(host="YOUR_PROXMOX_HOST"),
        description="Proxmox configuration"
    )
    local_ai: LocalAIConfig = Field(
        default_factory=LocalAIConfig,
        description="Local AI model configuration"
    )
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration"
    )
    
    # Feature flags
    enable_ai_generation: bool = Field(True, description="Enable AI code generation")
    enable_vm_operations: bool = Field(True, description="Enable VM operations")
    enable_metrics: bool = Field(False, description="Enable metrics collection")
    
    # Environment-specific settings
    environment: str = Field("development", description="Environment name")
    
    def __init__(self, **kwargs):
        """Initialize settings and create required directories."""
        super().__init__(**kwargs)
        self._create_directories()
        self._validate_configuration()
        
        logger.info(
            "Settings initialized",
            environment=self.environment,
            debug=self.debug,
            proxmox_host=self.proxmox.host
        )
    
    def _create_directories(self) -> None:
        """Create required directories if they don't exist."""
        for directory in [self.config_dir, self.data_dir, self.cache_dir]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug("Directory created", path=str(directory))
            except Exception as e:
                logger.error("Failed to create directory", path=str(directory), error=str(e))
                raise
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings."""
        # Validate logging configuration
        if self.logging.file_path:
            try:
                self.logging.file_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error("Failed to create log directory", error=str(e))
                raise
    
    @property
    def config_file(self) -> Path:
        """Get configuration file path."""
        return self.config_dir / "config.toml"
    
    @property
    def credentials_file(self) -> Path:
        """Get credentials file path."""
        return self.config_dir / "credentials.json"
    
    def get_proxmox_url(self) -> str:
        """Get complete Proxmox API URL."""
        protocol = "https" if self.proxmox.verify_ssl else "http"
        return f"{protocol}://{self.proxmox.host}:{self.proxmox.port}/api2/json"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() in ("production", "prod")
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() in ("development", "dev")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)."""
        data = self.model_dump()
        return data
    


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance (singleton pattern).
    
    Returns:
        Settings: Application settings
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from configuration files.
    
    Returns:
        Settings: Reloaded application settings
    """
    global _settings
    _settings = Settings()
    logger.info("Settings reloaded")
    return _settings