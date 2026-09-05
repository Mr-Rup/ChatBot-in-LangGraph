"""
Centralized logging configuration for the ChatBot application.

Call setup_logging() once at application startup (in app.py) before any
other module is imported. After that, every module can simply do:

    import logging
    logger = logging.getLogger(__name__)

and its output will automatically use this format and go to the right place.

Log format
----------
Each line looks like:

    2026-09-05 12:30:45 | ERROR    | backend.graph.builder :: chat_node() line 142
    Failed to invoke LLM
    Traceback (most recent call last):
      ...

Fields:
  - Timestamp         (human-readable local time)
  - Level             (DEBUG / INFO / WARNING / ERROR / CRITICAL)
  - Module path       (backend.graph.builder — matches the Python import path)
  - Function name     (chat_node)
  - Line number       (142)
  - Message
  - Full traceback    (only on ERROR / CRITICAL, when exc_info=True is used)
"""

# Standard library
import logging
import logging.handlers
import os
import sys
from typing import Optional


# ============================================================
# Custom Formatter
# ============================================================

class _PreciseFormatter(logging.Formatter):
    """
    A log formatter that shows the exact source location on a dedicated line
    so you can navigate directly to the problem with one glance.

    Output format (two lines per record):
        {timestamp} | {LEVEL:<8} | {module} :: {function}() line {lineno}
        {message}
        {traceback}   ← only present on ERROR/CRITICAL when exc_info is used
    """

    # ANSI color codes for terminal output (disabled if not a TTY)
    _COLORS = {
        "DEBUG":    "\033[36m",   # Cyan
        "INFO":     "\033[32m",   # Green
        "WARNING":  "\033[33m",   # Yellow
        "ERROR":    "\033[31m",   # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    _RESET = "\033[0m"

    def __init__(self, use_color: bool = True):
        super().__init__()
        self._use_color = use_color and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        # Timestamp
        timestamp = self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")

        # Level with optional ANSI color
        level = record.levelname
        if self._use_color and level in self._COLORS:
            colored_level = f"{self._COLORS[level]}{level:<8}{self._RESET}"
        else:
            colored_level = f"{level:<8}"

        # Source location: module + function + line
        location = f"{record.name} :: {record.funcName}() line {record.lineno}"

        # Compose the header line
        header = f"{timestamp} | {colored_level} | {location}"

        # Message body
        message = record.getMessage()

        # Traceback (if the caller passed exc_info=True or used logger.exception)
        if record.exc_info:
            tb = self.formatException(record.exc_info)
            return f"{header}\n  {message}\n{tb}"

        return f"{header}\n  {message}"


# ============================================================
# Public Setup Function
# ============================================================

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure the root logger for the entire application.

    Must be called once at startup (in app.py) before any module is imported.
    Subsequent calls are idempotent — handlers are not added twice.

    Parameters
    ----------
    level : int
        The minimum log level to capture. Defaults to logging.INFO.
        Pass logging.DEBUG to see tool discovery details.
    log_file : str or None
        If provided, logs are also written to this file path (rotating,
        max 2 MB, keeps 3 backups). Useful for debugging crashes after
        the terminal closes.
    """
    root_logger = logging.getLogger()

    # Avoid adding duplicate handlers on Streamlit reruns
    if root_logger.handlers:
        return

    root_logger.setLevel(level)

    # ── Console handler (stderr — visible in the terminal where streamlit runs) ──
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(_PreciseFormatter(use_color=True))
    root_logger.addHandler(console_handler)

    # ── Optional file handler (plain text, no colors) ──
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=2 * 1024 * 1024,   # 2 MB per file
            backupCount=3,               # Keep chatbot.log, chatbot.log.1, .log.2, .log.3
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        # No color in file output
        file_handler.setFormatter(_PreciseFormatter(use_color=False))
        root_logger.addHandler(file_handler)

    # Silence overly verbose third-party loggers that flood the output
    # but keep WARNING+ so serious issues from these libraries still surface.
    for noisy_lib in ("urllib3", "httpx", "httpcore", "transformers", "torch"):
        logging.getLogger(noisy_lib).setLevel(logging.WARNING)

    root_logger.info(
        "Logging initialized — level=%s%s",
        logging.getLevelName(level),
        f", file={log_file}" if log_file else "",
    )
