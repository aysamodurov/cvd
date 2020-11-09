'''расчет статистических показателей'''
def calculate_coef_aprox(x):
    '''
    расчет коеффициентов А, В по МНК
    для равномерно распределенных точек(каждую секунду)
    '''
    print('calculate A,B for MNK')
    if not x:
        return
    sumX = 0
    sumI = 0
    sumXI = 0
    sumI2 = 0
    n = len(x)
    for (i, val) in enumerate(x):
        i += 1
        sumX += val
        sumI += i
        sumXI += val * i
        sumI2 += i * i
    a = (n * sumXI - sumX * sumI) / (n * sumI2 - sumI ** 2)
    b = 1 / n *(sumX - a * sumI)
    xMean = a * n/2 + b
    std = 0
    for val in x:
        std += (xMean - val) ** 2
    std = (std/(n-1)) ** 0.5
    print(xMean)
    print(std)
    return a, b
