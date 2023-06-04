"""
The module includes a tool to generate a personalized logging tool
"""

import os
import logging
from settings import LoggerPaths



def setup_logger(
    name: str, log_file_name: str, level_of_log=logging.INFO, print_logs: bool = False
    ) -> logging.Logger:
    """
    Set up a logger with the specified name, log file, log level, and print option.

    Args:
        name (str): Name of the logger.
        log_file_name (str): Name of the log file.
        level_of_log (int, optional): Log level (default is logging.INFO).
        print_logs (bool, optional): Whether to print logs to console (default is False).

    Returns:
        logging.Logger: Configured logger object.

    """

    log_path = os.path.join(LoggerPaths().log_path, log_file_name)
    if not os.path.isfile(log_path):
        with open(log_path, "w", encoding="utf-8"):
            pass

    logger = logging.getLogger(name)
    message_format = logging.Formatter(
        "%(asctime)s.%(msecs)04d - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(message_format)
    logger.setLevel(level_of_log)
    logger.addHandler(file_handler)

    if print_logs is True:
        logger.addHandler(logging.StreamHandler())

    return logger
