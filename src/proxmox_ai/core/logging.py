"""
Structured logging configuration for Proxmox AI Assistant.

Provides secure, structured logging with proper filtering of sensitive data
and integration with monitoring systems.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.typing import Processor

from .config import LoggingConfig


class SensitiveDataFilter:
    """Filter to remove sensitive data from log records."""
    
    SENSITIVE_KEYS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
        'authorization', 'credential', 'api_key', 'private_key',
        'session_id', 'csrf_token', 'cookie'
    }
    
    def __call__(self, logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive data from event dictionary."""
        return self._filter_dict(event_dict)
    
    def _filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter sensitive data from dictionary."""
        filtered = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if key is sensitive
            if any(sensitive in key_lower for sensitive in self.SENSITIVE_KEYS):
                filtered[key] = "***REDACTED***"
            elif isinstance(value, dict):
                filtered[key] = self._filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    self._filter_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        
        return filtered


class SecurityAuditProcessor:
    """Processor for security audit events."""
    
    def __call__(self, logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Add security audit metadata to events."""
        # Add security context if this is a security-related event
        event = event_dict.get('event', '')
        if any(keyword in event.lower() for keyword in [
            'auth', 'login', 'credential', 'permission', 'access', 'security'
        ]):
            event_dict['audit'] = True
            event_dict['security_event'] = True
        
        return event_dict


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        config: Logging configuration. If None, uses default configuration.
    """
    if config is None:
        config = LoggingConfig()
    
    # Configure structlog processors
    processors: list[Processor] = [
        # Filter sensitive data first
        SensitiveDataFilter(),
        
        # Add security audit metadata
        SecurityAuditProcessor(),
        
        # Add standard structlog processors
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Configure output format
    if config.format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=sys.stderr.isatty(),
                exception_formatter=structlog.dev.plain_traceback
            )
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=getattr(logging, config.level),
    )
    
    # Set up file handler if specified
    if config.file_path:
        _setup_file_logging(config)
    
    # Configure third-party loggers
    _configure_third_party_loggers(config)
    
    logger = structlog.get_logger(__name__)
    logger.info(
        "Logging configured",
        level=config.level,
        format=config.format,
        file_logging=bool(config.file_path)
    )


def _setup_file_logging(config: LoggingConfig) -> None:
    """Set up file-based logging with rotation."""
    if not config.file_path:
        return
    
    # Create log directory if it doesn't exist
    config.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=config.file_path,
        maxBytes=config.max_file_size,
        backupCount=config.backup_count,
        encoding='utf-8'
    )
    
    # Set format for file handler
    if config.format == "json":
        formatter = logging.Formatter('%(message)s')
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, config.level))
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def _configure_third_party_loggers(config: LoggingConfig) -> None:
    """Configure logging levels for third-party libraries."""
    # Reduce noise from third-party libraries
    third_party_loggers = {
        'urllib3': 'WARNING',
        'requests': 'WARNING',
        'httpx': 'WARNING',
        'aiohttp': 'WARNING',
        'asyncio': 'WARNING',
        'proxmoxer': 'INFO',
    }
    
    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(getattr(logging, level))


def get_security_logger() -> Any:
    """
    Get a logger specifically for security events.
    
    Returns:
        Structured logger configured for security auditing
    """
    return structlog.get_logger("security")


def log_security_event(
    event: str,
    success: bool = True,
    user: Optional[str] = None,
    resource: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a security-related event.
    
    Args:
        event: Description of the security event
        success: Whether the event was successful
        user: User associated with the event
        resource: Resource that was accessed/modified
        details: Additional event details
    """
    logger = get_security_logger()
    
    log_data = {
        'event': event,
        'success': success,
        'audit': True,
        'security_event': True
    }
    
    if user:
        log_data['user'] = user
    if resource:
        log_data['resource'] = resource
    if details:
        log_data.update(details)
    
    if success:
        logger.info("Security event", **log_data)
    else:
        logger.warning("Security event failed", **log_data)


def log_api_call(
    method: str,
    endpoint: str,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    user: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """
    Log an API call.
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration: Request duration in seconds
        user: User making the request
        error: Error message if request failed
    """
    logger = structlog.get_logger("api")
    
    log_data = {
        'method': method,
        'endpoint': endpoint,
        'api_call': True
    }
    
    if status_code:
        log_data['status_code'] = status_code
    if duration:
        log_data['duration'] = duration
    if user:
        log_data['user'] = user
    if error:
        log_data['error'] = error
    
    if error or (status_code and status_code >= 400):
        logger.error("API call failed", **log_data)
    else:
        logger.info("API call", **log_data)