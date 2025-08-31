"""
Logging utilities for View-from-CSV

PROVIDES: Consistent logging interface across the application
DEPENDS: Standard library only
CONSUMED BY: All modules that need logging
CONTRACT: Provides structured logging with configurable levels
TECH CHOICE: Standard logging with custom formatters
RISK: Low - standard Python logging
TODO(NEXT): Add log file rotation and structured logging
"""

import logging
import sys
from typing import Optional
from pathlib import Path

# =========================
# LOGGING CONFIGURATION
# =========================

def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    debug: bool = False
) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        debug: Enable debug mode (overrides level)
    
    Returns:
        Configured logger instance
    """
    # Set log level
    if debug:
        level = "DEBUG"
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("x987")
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file {log_file}: {e}")
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance for the specified name"""
    if name:
        return logging.getLogger(f"x987.{name}")
    return logging.getLogger("x987")

# =========================
# LOGGING DECORATORS
# =========================

def log_function_call(logger: Optional[logging.Logger] = None):
    """Decorator to log function calls with parameters"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            log.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                log.debug(f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                log.error(f"{func.__name__} failed with error: {e}")
                raise
        return wrapper
    return decorator

def log_execution_time(logger: Optional[logging.Logger] = None):
    """Decorator to log function execution time"""
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                log.info(f"{func.__name__} completed in {execution_time:.2f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                log.error(f"{func.__name__} failed after {execution_time:.2f}s with error: {e}")
                raise
        return wrapper
    return decorator

# =========================
# PROGRESS LOGGING
# =========================

class ProgressLogger:
    """Helper class for logging progress of long-running operations"""
    
    def __init__(self, logger: logging.Logger, total: int, operation: str):
        self.logger = logger
        self.total = total
        self.operation = operation
        self.current = 0
        self.last_logged = 0
        self.log_interval = max(1, total // 10)  # Log every 10% or every item
    
    def update(self, count: int = 1):
        """Update progress counter"""
        self.current += count
        
        # Log progress at intervals
        if self.current - self.last_logged >= self.log_interval:
            percentage = (self.current / self.total) * 100
            self.logger.info(f"{self.operation}: {self.current}/{self.total} ({percentage:.1f}%)")
            self.last_logged = self.current
    
    def complete(self):
        """Mark operation as complete"""
        self.logger.info(f"{self.operation}: Completed {self.current}/{self.total} items")
    
    def error(self, error_msg: str):
        """Log error during operation"""
        self.logger.error(f"{self.operation}: Error at {self.current}/{self.total}: {error_msg}")

# =========================
# UTILITY FUNCTIONS
# =========================

def log_memory_usage(logger: logging.Logger):
    """Log current memory usage"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logger.debug(f"Memory usage: {memory_mb:.1f} MB")
    except ImportError:
        logger.debug("psutil not available, cannot log memory usage")

def log_system_info(logger: logging.Logger):
    """Log system information for debugging"""
    import platform
    
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.architecture()}")
    
    try:
        import psutil
        logger.info(f"CPU cores: {psutil.cpu_count()}")
        logger.info(f"Memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB")
    except ImportError:
        logger.debug("psutil not available, cannot log system info")
