#!/usr/bin/env python3
"""
Structured Logging System for TECH INTERACTIVE
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys


class Logger:
    """Centralized logging system"""

    def __init__(self, log_dir: str = "logs", level: int = logging.INFO):
        """Initialize logging system"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.level = level
        self.loggers = {}
        self._setup_root_logger()

    def _setup_root_logger(self) -> None:
        """Setup root logger with file and console handlers"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.level)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # File handler for all logs
        events_file = self.log_dir / 'events.log'
        file_handler = logging.handlers.RotatingFileHandler(
            events_file, maxBytes=10485760, backupCount=10
        )
        file_handler.setLevel(self.level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with file handler"""
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)

        # Create specific log file for each module
        log_file = self.log_dir / f"{name}.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        handler.setLevel(self.level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.loggers[name] = logger
        return logger


# Global logger instance
_logger_instance: Optional[Logger] = None


def init_logger(log_dir: str = "logs", level: int = logging.INFO) -> Logger:
    """Initialize global logger"""
    global _logger_instance
    _logger_instance = Logger(log_dir, level)
    return _logger_instance


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    global _logger_instance
    if _logger_instance is None:
        init_logger()
    return _logger_instance.get_logger(name)
