"""
Инициализация логгера
"""
import logging
import os
import config


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


def init_logger():
    """
    Инициализация объекта логгера
    """
    log_foldername = init_logs_folder()
    log_filename = f'{log_foldername}/{__name__}.log'
    # logging.basicConfig(level=logging.INFO, filename=log_filename, filemode='w', format=_log_format)
    logging.basicConfig(level=logging.INFO, handlers=[get_stream_handler(), get_file_handler()], format=_log_format)

def init_logs_folder():
    """
        Получение пути к директории для логгирования
        из файла конфигурации проекта
        и создане этой папки в случае если ее нет

        Returns:
            str: Путь к директории для логгирования
    """
    log_foldername = config.read_value('logsFile', 'logFolder')
    if not os.path.exists(log_foldername):
        os.mkdir(log_foldername)
    return log_foldername
