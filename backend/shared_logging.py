"""
Centralized logging configuration for GrabOn BNPL Backend.

Consolidates all logs from:
- MCP Server (tool calls, credit scoring, eligibility checks)
- API Server (HTTP requests, PayU client, checkout flow)
- PayU Client (EMI calculations, sandbox API calls)
- All backend operations

All logs are written to: backend/logs/grabon_bnpl.log
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Centralized log file path
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "grabon_bnpl.log"

# Log format with timestamps and detailed context
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)-25s | "
    "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    logger_name: str = None,
    level: str = "INFO",
    console_output: bool = True
) -> logging.Logger:
    """
    Configure centralized logging for backend components.

    Args:
        logger_name: Name of the logger (e.g., "api", "mcp-server", "payu-client")
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to also output logs to console

    Returns:
        Configured logger instance

    Example:
        >>> from shared_logging import setup_logging
        >>> logger = setup_logging("api")
        >>> logger.info("API server started")
    """
    # Get or create logger
    logger = logging.getLogger(logger_name or __name__)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    # File handler: Rotating log file (max 10MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Capture everything in file
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (optional, for development)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        console_formatter = logging.Formatter(
            "%(levelname)-8s | %(name)-20s | %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def log_section_separator(logger: logging.Logger, section_name: str):
    """
    Log a visual separator for major sections (API startup, MCP tool call, etc.)

    Args:
        logger: Logger instance
        section_name: Name of the section (e.g., "API SERVER STARTUP")
    """
    separator = "=" * 80
    logger.info(separator)
    logger.info(f"  {section_name}")
    logger.info(separator)


def log_api_request(logger: logging.Logger, method: str, path: str, user_id: str = None):
    """
    Log API request in structured format.

    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        user_id: User ID if available
    """
    user_context = f" | User: {user_id}" if user_id else ""
    logger.info(f"[API REQUEST] {method} {path}{user_context}")


def log_mcp_tool_call(logger: logging.Logger, tool_name: str, params: dict = None):
    """
    Log MCP tool call with parameters.

    Args:
        logger: Logger instance
        tool_name: Name of the MCP tool
        params: Tool parameters
    """
    params_str = f" | Params: {params}" if params else ""
    logger.info(f"[MCP TOOL] {tool_name}{params_str}")


def log_payu_api_call(logger: logging.Logger, endpoint: str, user_id: str, amount: float):
    """
    Log PayU API call.

    Args:
        logger: Logger instance
        endpoint: PayU API endpoint
        user_id: User ID
        amount: Transaction amount
    """
    logger.info(f"[PAYU API] {endpoint} | User: {user_id} | Amount: Rs.{amount:,.2f}")


def log_eligibility_check(
    logger: logging.Logger,
    user_id: str,
    amount: float,
    status: str,
    credit_limit: float = None
):
    """
    Log credit eligibility check result.

    Args:
        logger: Logger instance
        user_id: User ID
        amount: Purchase amount
        status: Eligibility status (approved, rejected, etc.)
        credit_limit: Approved credit limit if applicable
    """
    limit_str = f" | Limit: Rs.{credit_limit:,.0f}" if credit_limit else ""
    logger.info(
        f"[ELIGIBILITY CHECK] {user_id} | Amount: Rs.{amount:,.2f} | "
        f"Status: {status.upper()}{limit_str}"
    )


# Initialize root logger on module import
root_logger = setup_logging("grabon-bnpl", level="INFO", console_output=True)
log_section_separator(root_logger, f"GRABON BNPL BACKEND - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
