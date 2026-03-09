import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(log_name, log_file, level=logging.INFO, max_bytes=5000000, backup_count=5):
    """Sets up a logger with a rotating file handler.

    Args:
        log_name (str): Name of the logger.
        log_file (_type_): Path to the log file.
        level (_type_, optional): Log level. Defaults to logging.INFO.
        max_bytes (int, optional): Maximum byte value. Defaults to 5000000.
        backup_count (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    # Rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(level)

    # Stream handler for console output
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)

    # Formatter for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Adding both handlers to the logger
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
