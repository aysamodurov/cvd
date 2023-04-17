import config
import time
import logging


log = logging.getLogger(__name__)


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


def singleton(cls):
    """

    Декоратор для создания Singleton

    """
    _instanse = {}
    def wrapper(*args, **kwargs):
        if cls not in _instanse:
            _instanse[cls] = cls(*args, **kwargs)
        return _instanse[cls]
    return wrapper

def formatting_number(num, prec=None):
    '''
    Форматирование числа в строку

    Parameters
    ----------
    num (float) : Чисто 
    prec (int) : Количество знаков после запятой
    Если оно не указано, то осуществляется автоматический выбор

    Returns
    -------
    str: отформатированная для печати строка

    '''
    #определяется количество знаков после запятой
    if prec == None:
        try:
            prec = int(config.read_value('formatting', 'precision', 3)) + 1
            prec = prec - len(str(int(num)))
            if prec < 0:
                prec = 0
            num = float(num)
        except ValueError:
            log.warning(f'Невозможно преобразовать в число {num} ')
            prec = 0
    res = '{:{width}.{pr}f}'.format(num,  width=3, pr=prec)
    
    # Удаляю незначащии нули
    while res and (set(res) & set('.,')) and res[-1] in ['0', '.', '.']:
        res = res[:-1]
    if not res or res == '-0':
        res = '0'
    
    return res
