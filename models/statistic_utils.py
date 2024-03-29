
def calcMNK(x):
    '''
    расчет коеффициентов А, В по МНК
    для равномерно распределенных точек (каждую секунду)
    в массиве x
    возвращается коэффициенты A,B для выражения A*x+B
    '''
    n = len(x)
    if n == 1:
        return 0, x[0]
    sumX, sumI, sumXI, sumI2 = [0]*4
    for (i, val) in enumerate(x):
        i += 1
        sumX += val
        sumI += i
        sumXI += val * i
        sumI2 += i * i
    a = (n * sumXI - sumX * sumI) / (n * sumI2 - sumI ** 2)
    b = 1 / n * (sumX - a * sumI)
    return (a, b)


def calcMNKMean(x):
    '''
    расчет коеффициентов А, В по МНК
    для равномерно распределенных точек (каждую секунду)
    в массиве x
    возвращается значение в середине интервала A*x+B
    '''
    if x:
        a, b = calcMNK(x)
        return a * len(x) / 2 + b


def calcSKO(x, xMean):
    '''
    расчет СКО
    для равномерно распределенных точек (каждую секунду)
    x - массив данных
    xmean- среднее значение
    возвращается СКО
    '''
    if not x:
        return 0
    n = len(x)
    if n == 1:
        return 0
    std = 0
    for val in x:
        std += (xMean - val) ** 2
    std = (std / (n - 1)) ** 0.5
    return std


def calcError(sko, countPoint):
    '''
    расчет погрешности = sko * k,
    k - коэффициент Стьюдента(0,95; количество точек - 1)
    '''
    return sko * getCoefStudent(countPoint-1)


def getCoefStudent(f):
    '''
    расчет коэффициента Стьюдента с доверительной вероятностью 0,95
    и f степеней свободы(количество значений -1)
    '''
    fList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
             18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34,
             36, 38, 40, 42, 44, 46, 48, 50, 55, 60, 65, 70, 80, 90, 100,
             120, 150, 200, 250, 300, 400, 500]
    kSudentList = [12.71, 4.30, 3.18, 2.78, 2.57, 2.45, 2.36, 2.31, 2.26,
                   2.23, 2.20, 2.18, 2.16, 2.14, 2.13, 2.12, 2.11, 2.10,
                   2.09, 2.09, 2.08, 2.07, 2.07, 2.06, 2.06, 2.06, 2.05,
                   2.05, 2.05, 2.04, 2.04, 2.03, 2.03, 2.02, 2.02, 2.02,
                   2.02, 2.01, 2.01, 2.01, 2.00, 2.00, 2.00, 1.99, 1.99,
                   1.99, 1.98, 1.97, 1.98, 1.97, 1.97, 1.97, 1.97, 1.96]
    for (i, fVal) in enumerate(fList):
        if f <= fVal:
            return kSudentList[i]
    # если количество степеней свободы больше 600
    return kSudentList[-1]


def calc_outliers(values, delta, mean = 0):
    '''
    Расчет количество выбросов

    Parameters
    ----------
    values : Список значений 
    delta : Допустимая погрешность
    mean : Среднее значение спсика

    Returns
    -------
    float
        Процент выбросов (резко выделяющихся значений)

    '''
    if mean == 0:
        mean = calcMNKMean(values)
    
    if delta == 0:
        return 0
   
    res = 0
    max_delta = 2 * delta
    for val in values:
        if abs(val - mean) > max_delta:
            res += 1
    try:
        res = 100 * res / len(values)
    except ZeroDivisionError:
        res = 0
    return res


def calc_rate_of_change(values):
    '''
    Расчет скорости изменения параметра

    Parameters
    ----------
    values : Список значений 

    Returns
    -------
    res (float): Скорость изменения параметра 

    '''
    res, _ = calcMNK(values)
    return 3600 * res
