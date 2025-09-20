"""
DevLogger Utility
Author: larscd
Description:
    A reusable logging utility designed for game development and other Python projects.
    Provides configurable logging to both console and file, with a consistent format.
    Supports multiple independent loggers without duplication of handlers.
"""

import logging
import os
from datetime import datetime
from typing import Type, Optional

from data.config.config_settings import DEV_SETTINGS


class DevLogger:
    """
    DevLogger is a reusable logging utility class for development purposes.

    Features:
        - Configurable logging to console and file.
        - Timestamped log files to avoid overwriting.
        - Prevents duplicate log entries from multiple class instances.
        - Controlled enable/disable logging via external config (DEV_SETTINGS).

    Attributes:
        logger_enabled (bool): Whether logging is enabled, taken from DEV_SETTINGS.
        logger (logging.Logger): The configured Python logger instance.
        log_file_path (str): Path to the log file for this logger instance.
    """

    _initialized_loggers = set()  # Tracks initialized logger names to prevent duplicate handlers.


    def __init__(
        self,
        logging_class: Type,
        log_level: int = logging.DEBUG,
        print_level: int = logging.INFO,
        log_dir: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        """
        Initialize the DevLogger

        :param logging_class:
        :param log_level:
        :param print_level:
        :param log_dir:
        :param enabled:
        """

        self.logger_enabled = enabled if enabled is not None else DEV_SETTINGS['logging_enabled']

        # Setup log directory
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.logging_dir = log_dir if log_dir else DEV_SETTINGS['logging_dir']
        os.makedirs(os.path.join(self.cwd, self.logging_dir), exist_ok=True)

        # Unique logger name per class/module
        logger_name = str(logging_class.__name__)
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(min(print_level, log_level))  # Ensure logger processes both levels

        # Avoid re-adding handlers if logger already initialized
        if logger_name not in self._initialized_loggers:
            self._setup_handlers(logger_name, log_level, print_level)
            self._initialized_loggers.add(logger_name)


    def _setup_handlers(self, logger_name: str, log_level: int, print_level: int):
        """
        Setup console and file handlers for the logger

        :param logger_name:
        :param log_level:
        :param print_level:
        :return:
        """
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(print_level)
        console_formatter = logging.Formatter("[%(levelname)s][%(asctime)s]: %(name)s > %(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler
        time_start = datetime.now().strftime("%Y-%m-%d_%Hh-%Mm-%Ss")
        log_file_path = os.path.join(
            self.cwd, self.logging_dir, f"dev-log-{logger_name}-{time_start}.txt"
        )
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter("[%(levelname)s][%(asctime)s]: %(name)s > %(message)s")
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        self.log_file_path = log_file_path


    def log(self, level: int, message: str):
        """
        Log a message at the specified level

        :param level:
        :param message:
        :return:
        """
        if self.logger_enabled:
            self.logger.log(level, message)


    def debug(self, message: str):
        """Shortcut for debug logging."""
        self.log(logging.DEBUG, message)


    def info(self, message: str):
        """Shortcut for info logging."""
        self.log(logging.INFO, message)


    def warning(self, message: str):
        """Shortcut for warning logging."""
        self.log(logging.WARNING, message)


    def error(self, message: str):
        """Shortcut for error logging."""
        self.log(logging.ERROR, message)


    def critical(self, message: str):
        """Shortcut for critical logging."""
        self.log(logging.CRITICAL, message)
