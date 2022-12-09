import time
import app_logger

log = app_logger.get_logger(__name__)


def timer(func):
    """
        Декоратор для вычисления времени работы функции
    """

    def wrapper(*args):
        start = time.time()
        res = func(*args)
        end = time.time()
        log.info('Время работы функции {} - {} секунд'.format(func, end-start))
        return res
    return wrapper
