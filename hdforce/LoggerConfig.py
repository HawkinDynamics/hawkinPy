import logging

class LoggerConfig:
    @staticmethod
    def Configure(level='info', file=False, file_path='hdforce.log', file_mode='a'):
        """
        Configures the logging for the entire application.
        
        Parameters:
        - level: Logging level as a string ('debug', 'info', 'warning', 'error', 'critical').
        - file: Boolean to determine if logging to a file should be enabled.
        - file_path: Path to the log file.
        - file_mode: Mode to open the log file (e.g., 'w' for overwrite, 'a' for append).
        """
        # Set up the root logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Clear existing handlers
        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')

        # Optionally add a file handler
        if file:
            file_handler = logging.FileHandler(file_path, mode=file_mode)
            file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            # Create and add the stream handler
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    @staticmethod
    def get_logger(module_name):
        """
        Retrieve a logger for a specific module.
        
        Parameters:
        - module_name: Name of the module requesting the logger.
        
        Returns:
        - Configured Logger object.
        """
        return logging.getLogger(module_name)