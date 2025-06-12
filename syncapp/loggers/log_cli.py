#loggers/log_cli.py
import logging
from pathlib import Path
from syncapp.config.logfile import create_log_file
import sys

def setup_logger(name=__name__, logfile=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # Console handler with UTF-8 encoding
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Use the log file from logfile.py if no specific logfile is provided
        if logfile is None:
            logfile = create_log_file()
        
        # Ensure the log directory exists
        log_path = Path(logfile)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(logfile, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
