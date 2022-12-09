
import time


def timer(func):
    """Декоратор для вычисления времени работы функции
    """

    def wrapper(*args):
        start = time.time()
        res = func(*args)
        end = time.time()
        print('Время работы функции {} - {} секунд'.format(func, end-start))
        return res
    return wrapper
