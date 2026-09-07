"""Logging configuration for the application."""

import logging
import logging.handlers
import sys
from pathlib import Path
from app.config import settings

# Create logs directory
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file paths
APP_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
DEBUG_LOG_FILE = LOG_DIR / "debug.log"


def setup_logging() -> None:
    """Configure logging for the application."""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.debug_enabled else logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Log format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Use UTF-8 on Windows so model responses containing Unicode cannot break
    # console logging. Replacement keeps logging non-fatal for odd characters.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO if not settings.debug_enabled else logging.DEBUG)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File Handler - Application Logs
    try:
        app_file_handler = logging.handlers.RotatingFileHandler(
            APP_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        app_file_handler.setLevel(logging.INFO)
        app_file_handler.setFormatter(log_format)
        root_logger.addHandler(app_file_handler)
    except Exception as e:
        logging.warning(f"Failed to setup app log file handler: {e}")
    
    # File Handler - Error Logs
    try:
        error_file_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(log_format)
        root_logger.addHandler(error_file_handler)
    except Exception as e:
        logging.warning(f"Failed to setup error log file handler: {e}")
    
    # File Handler - Debug Logs (only in development)
    if settings.debug_enabled:
        try:
            debug_file_handler = logging.handlers.RotatingFileHandler(
                DEBUG_LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=3,
            )
            debug_file_handler.setLevel(logging.DEBUG)
            debug_file_handler.setFormatter(log_format)
            root_logger.addHandler(debug_file_handler)
        except Exception as e:
            logging.warning(f"Failed to setup debug log file handler: {e}")
    
    # Suppress verbose logs from third-party libraries
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("groq").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("jose").setLevel(logging.WARNING)
    
    root_logger.info(f"Logging initialized - Environment: {settings.ENVIRONMENT}")


# Initialize logging when module is imported
setup_logging()

# Get logger for use in modules
logger = logging.getLogger(__name__)
