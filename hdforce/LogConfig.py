import logging

#--------------------#
# Logger
class LoggerConfig:
    """A class for configuring logging for the application.

    Attributes:
        configured (bool): Class variable to track if logging has been configured manually.
    """
    configured = False  # Class variable to track if logging has been configured manually

    def __init__(self, file: bool = False, level: str = 'info'):
        """
        Initialize the LoggerConfig class and set up the logger.

        Parameters:
            file (bool): Whether to log to a file. If True, logs are written to 'hdforce.log'. If False, logs are written to stdout.
            level (str): The log level as a string. Expected values are 'debug', 'info', 'warning', 'error', or 'critical'.
        """
        self.file = file
        self.level = level
        self.setup_logger(file, level)
        LoggerConfig.configured = True

    @staticmethod
    def setup_logger(file=False, level='info'):
        """
        Set up the logger based on the specified file flag and log level.

        Parameters:
            file (bool): If True, create a file handler. Otherwise, create a console handler.
            level (str): The logging level ('debug', 'info', 'warning', 'error', 'critical').

        Returns:
            logging.Logger: The configured logger object.
        """
        logger = logging.getLogger('hdforce')
        logger.setLevel(logging.DEBUG)  # Set minimum level of logs to capture
        
        # Determine handler based on 'file' flag
        if file:
            handler = logging.FileHandler('hdforce.log')
        else:
            handler = logging.StreamHandler()
        
        # Set log level
        log_level = getattr(logging, level.upper(), logging.INFO)
        handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Clean up any old handlers if they exist
        if logger.handlers:
            for h in logger.handlers[:]:
                logger.removeHandler(h)

        logger.addHandler(handler)
        return logger

# User Controlled Log Config Function
def LogConfig(file: bool = False, level: str = 'info'):
    """
    Configure logging for the application based on user preferences or defaults.

    Parameters:
        file (bool): If True, logs will be written to a file. If False, logs will be written to stdout.
        level (str): Desired log level. Valid values are 'debug', 'info', 'warning', 'error', 'critical'.
    """
    LoggerConfig.setup_logger(file, level)