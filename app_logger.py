import logging
import os
import configparser


_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

def get_file_handler():
    log_foldername = init_logs_folder()
    file_handler = logging.FileHandler(f"{log_foldername}/{__name__}.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger

def init_logs_folder():
    config = configparser.ConfigParser()
    config.read('config/settings.ini')
    log_foldername = config['logsFile']['logFolder']
    if not os.path.exists(log_foldername):
        os.mkdir(log_foldername)
    return log_foldername