"""
Structured Logging with Emoji Indicators
"""

import structlog
import logging
import sys
from pathlib import Path
from typing import Any
from app.config import settings


def setup_logging() -> structlog.BoundLogger:
    """
    Configure structured logging with emoji indicators for visual clarity
    
    Features:
    - JSON format for production
    - Colored console for development
    - File rotation
    - Emoji indicators for quick visual parsing
    """
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure processors based on format
    if settings.log_format == "json":
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    else:
        # Console format with colors
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level.value)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=logging.getLevelName(settings.log_level.value),
        handlers=[]
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(
        logging.DEBUG if settings.debug_mode else logging.INFO
    )
    logging.root.addHandler(console_handler)
    
    # File handler with rotation
    if settings.log_to_file:
        try:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                settings.log_file_path,
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            logging.root.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")
    
    # Get logger instance
    logger = structlog.get_logger()
    
    # Log initialization
    logger.info(
        "🚀 Logging initialized",
        app_name=settings.app_name,
        version=settings.app_version,
        log_level=settings.log_level.value,
        debug_mode=settings.debug_mode,
        log_format=settings.log_format
    )
    
    return logger


# Global logger instance
logger = setup_logging()


# Convenience functions with emoji indicators
def log_agent_start(agent_name: str, **kwargs):
    """Log agent start with emoji"""
    logger.info(f"🤖 Agent Started: {agent_name}", agent=agent_name, **kwargs)


def log_agent_complete(agent_name: str, duration_ms: float, **kwargs):
    """Log agent completion with emoji"""
    logger.info(
        f"⏱️  Agent Completed: {agent_name}",
        agent=agent_name,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )


def log_agent_error(agent_name: str, error: Exception, **kwargs):
    """Log agent error with emoji"""
    logger.error(
        f"❌ Agent Failed: {agent_name}",
        agent=agent_name,
        error=str(error),
        error_type=type(error).__name__,
        **kwargs
    )


def log_llm_call(model: str, tokens: int, duration_ms: float, **kwargs):
    """Log LLM call with emoji"""
    logger.info(
        f"🧠 LLM Call",
        model=model,
        tokens=tokens,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )


def log_slow_operation(operation: str, duration_ms: float, threshold_ms: int, **kwargs):
    """Log slow operation with emoji"""
    logger.warning(
        f"🐌 Slow Operation: {operation}",
        operation=operation,
        duration_ms=round(duration_ms, 2),
        threshold_ms=threshold_ms,
        **kwargs
    )


def log_success(message: str, **kwargs):
    """Log success with emoji"""
    logger.info(f"✅ {message}", **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning with emoji"""
    logger.warning(f"⚠️  {message}", **kwargs)


def log_error(message: str, **kwargs):
    """Log error with emoji"""
    logger.error(f"❌ {message}", **kwargs)


def log_debug(message: str, **kwargs):
    """Log debug with emoji"""
    logger.debug(f"🔍 {message}", **kwargs)
