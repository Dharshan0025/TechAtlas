"""
Log Manager Utility
Centralized logging configuration and management
"""

import logging
import sys
from datetime import datetime
from typing import Optional
import os


class LogManager:
    """
    Manages application logging
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Log Manager"""
        if not LogManager._initialized:
            self.setup_logging()
            LogManager._initialized = True
    
    def setup_logging(self, log_level: str = 'INFO', log_file: Optional[str] = None):
        """
        Setup logging configuration
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
        """
        # Convert string level to logging constant
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup handlers
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        handlers.append(console_handler)
        
        # File handler (if specified)
        if log_file:
            try:
                # Create log directory if it doesn't exist
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(level)
                file_handler.setFormatter(detailed_formatter)
                handlers.append(file_handler)
            except Exception as e:
                print(f"Warning: Could not create log file handler: {e}")
        
        # Configure root logger
        logging.basicConfig(
            level=level,
            handlers=handlers,
            force=True
        )
        
        # Log initialization
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized at {log_level} level")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance
        
        Args:
            name: Logger name (usually __name__)
        
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    @staticmethod
    def log_request(method: str, path: str, user: str = 'anonymous'):
        """
        Log HTTP request
        
        Args:
            method: HTTP method
            path: Request path
            user: User identifier
        """
        logger = logging.getLogger('request')
        logger.info(f"{method} {path} - User: {user}")
    
    @staticmethod
    def log_response(method: str, path: str, status_code: int, duration_ms: float):
        """
        Log HTTP response
        
        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
        """
        logger = logging.getLogger('response')
        logger.info(f"{method} {path} - Status: {status_code} - Duration: {duration_ms:.2f}ms")
    
    @staticmethod
    def log_error(error: Exception, context: str = ''):
        """
        Log error with context
        
        Args:
            error: Exception object
            context: Additional context
        """
        logger = logging.getLogger('error')
        logger.error(f"{context} - {type(error).__name__}: {str(error)}", exc_info=True)
    
    @staticmethod
    def log_performance(operation: str, duration_ms: float, threshold_ms: float = 1000):
        """
        Log performance metrics
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            threshold_ms: Threshold for warning
        """
        logger = logging.getLogger('performance')
        
        if duration_ms > threshold_ms:
            logger.warning(f"SLOW: {operation} took {duration_ms:.2f}ms (threshold: {threshold_ms}ms)")
        else:
            logger.debug(f"{operation} took {duration_ms:.2f}ms")
    
    @staticmethod
    def log_security_event(event_type: str, user: str, details: str):
        """
        Log security-related events
        
        Args:
            event_type: Type of security event
            user: User involved
            details: Event details
        """
        logger = logging.getLogger('security')
        logger.warning(f"SECURITY [{event_type}] User: {user} - {details}")
    
    @staticmethod
    def log_audit(action: str, user: str, resource: str, details: dict = None):
        """
        Log audit trail
        
        Args:
            action: Action performed
            user: User who performed action
            resource: Resource affected
            details: Additional details
        """
        logger = logging.getLogger('audit')
        details_str = f" - Details: {details}" if details else ""
        logger.info(f"AUDIT [{action}] User: {user} - Resource: {resource}{details_str}")
    
    @staticmethod
    def set_level(logger_name: str, level: str):
        """
        Set logging level for specific logger
        
        Args:
            logger_name: Logger name
            level: Logging level
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    @staticmethod
    def disable_logger(logger_name: str):
        """Disable specific logger"""
        logger = logging.getLogger(logger_name)
        logger.disabled = True
    
    @staticmethod
    def enable_logger(logger_name: str):
        """Enable specific logger"""
        logger = logging.getLogger(logger_name)
        logger.disabled = False


# Global instance
log_manager = LogManager()
