import logging
import os
from datetime import datetime
import sys

class RangoLogger:
    """
    Centralized logging system for the Rango interpreter
    """

    
    def __init__(self, name="RangoInterpreter",debugFlag=False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.debugFlag=False

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers"""
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"rango_interpreter_{timestamp}.log"
        log_filepath = os.path.join(logs_dir, log_filename)
        
        # File handler - detailed logging
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler - important messages only
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # Set formatters
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log the start of session
        if(self.debugFlag):
            self.logger.info("="*80)
            self.logger.info("RANGO INTERPRETER SESSION STARTED")
            self.logger.info(f"Log file: {log_filepath}")
            self.logger.info("="*80)
    
    def debug(self, message, **kwargs):
        if(self.debugFlag):
            """Log debug message"""
            self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message, **kwargs):
        if(self.debugFlag):
            """Log info message"""
            self.logger.info(self._format_message(message, **kwargs))
        
    def warning(self, message, **kwargs):
        if(self.debugFlag):
            """Log warning message"""
            self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message, **kwargs):
        if(self.debugFlag):
            """Log error message"""
            self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message, **kwargs):
        if(self.debugFlag):
            """Log critical message"""
            self.logger.critical(self._format_message(message, **kwargs))
    
    def _format_message(self, message, **kwargs):
        """Format message with additional context"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message
    
    def log_tokenization_start(self, filename):
        if(self.debugFlag):
            """Log start of tokenization process"""
            self.info(f"Starting tokenization", filename=filename)
    
    def log_tokenization_complete(self, filename, token_count):
        if(self.debugFlag):
            """Log completion of tokenization"""
            self.info(f"Tokenization completed", filename=filename, tokens_generated=token_count)
    
    def log_tokenization_error(self, filename, error):
        if(self.debugFlag):
            """Log tokenization error"""
            self.error(f"Tokenization failed", filename=filename, error=str(error))
    
    def log_parsing_start(self, token_count):
        if(self.debugFlag):
            """Log start of parsing process"""
            self.info(f"Starting parsing", token_count=token_count)
    
    def log_parsing_complete(self, ast_type):
        if(self.debugFlag):
            """Log completion of parsing"""
            self.info(f"Parsing completed", ast_type=ast_type)
    
    def log_parsing_error(self, error):
        if(self.debugFlag):
            """Log parsing error"""
            self.error(f"Parsing failed", error=str(error))
    
    def log_interpretation_start(self):
        if(self.debugFlag):
            """Log start of interpretation process"""
            self.info("Starting interpretation")
    
    def log_interpretation_complete(self, result):
        if(self.debugFlag):
            """Log completion of interpretation"""
            self.info(f"Interpretation completed", result_type=type(result).__name__)
    
    def log_interpretation_error(self, error):
        if(self.debugFlag):
            """Log interpretation error"""
            self.error(f"Interpretation failed", error=str(error))
    
    def log_variable_assignment(self, var_name, value):
        if(self.debugFlag):
            """Log variable assignment"""
            self.debug(f"Variable assigned", variable=var_name, value=str(value))
    
    def log_variable_access(self, var_name, value):
        if(self.debugFlag):
            """Log variable access"""
            self.debug(f"Variable accessed", variable=var_name, value=str(value))
    
    def log_binary_operation(self, left, operator, right, result):
        if(self.debugFlag):
            """Log binary operation"""
            self.debug(f"Binary operation", left=str(left), operator=str(operator), right=str(right), result=str(result))
    
    def log_show_statement(self, values):
        if(self.debugFlag):
            """Log show statement execution"""
            self.debug(f"Show statement executed", values=[str(v) for v in values])
    
    def log_session_end(self):
        if(self.debugFlag):
            """Log end of session"""
            self.info("="*80)
            self.info("RANGO INTERPRETER SESSION ENDED")
            self.info("="*80)

# Global logger instance
_global_logger = None

def setup_logging(debugFlag=False):
    """Setup global logging instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = RangoLogger(debugFlag)
    return _global_logger

def get_logger(debugFlag=False):
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging(debugFlag)
    return _global_logger