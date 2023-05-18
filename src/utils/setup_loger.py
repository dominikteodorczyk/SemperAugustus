import logging

def setup_logger(name, log_file, level_of_log=logging.INFO, print = False):

    message_format = logging.Formatter(
        '%(asctime)s.%(msecs)04d - %(levelname)s: %(message)s', 
        '%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(message_format)

    logger = logging.getLogger(name)
    logger.setLevel(level_of_log)
    logger.addHandler(file_handler)

    if print is True:
        print_handler = logging.StreamHandler()
        logger.addHandler(print_handler)

    return logger