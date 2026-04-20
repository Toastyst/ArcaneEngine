import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file):
    logger = logging.getLogger()
    logger.handlers = []
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def log_error(msg):
    logging.error(msg)

def log_info(msg):
    logging.info(msg)