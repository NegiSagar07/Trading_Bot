"""Centralized logging configuration for the trading bot."""

from __future__ import annotations

import logging
from pathlib import Path

_LOGGER_NAME = "trading_bot"
_REPO_ROOT = Path(__file__).resolve().parent.parent


def configure_logging(log_file: str = "trading_bot.log") -> logging.Logger:
    """Configure console and file logging.

    Console output uses INFO level with a compact format.
    File output uses DEBUG level with a detailed format.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    log_path = _REPO_ROOT / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
