import numpy as np


def get_optimal_detector_time(detector, times=60):
    '''
        Выбор времени для обработки
        с минимальной скорость и случайной погрешностью
        detector - датчик
        times - количество точек, которые необходимо выбрать
        return дата начала и окончания промежутка с оптимальными для данных временами
    '''
    valueList = np.array(detector.get_value_list())
    if len(valueList) <= times:
        print('Недостаточная выборка данных')
        return (None, None)
    optimal_pos = 0
    min_sko = valueList[:times].std()
    for i in range(1, len(valueList) - times):
        sko = valueList[i:i + times].std()
        if sko < min_sko:
            min_sko = sko
            optimal_pos = i
    dtList = detector.get_date_list()
    return (dtList[optimal_pos], dtList[optimal_pos + times])

def get_optimal_time(detectorList, times=60):
    '''
    Выбор времени для обработки
    с минимальной скорость и случайной погрешностью
    detectorList - датчик
    times - количество точек, которые необходимо выбрать
    return дата начала и окончания промежутка с оптимальными для данных временами
    '''
    valueList = []
    for detector in detectorList:
        valueList.append(np.array(detector.get_value_list()))
    optimal_pos = 0
    min_sko = -1
    #поиск участка данных с минимальным СКО
    #оцениваются все датчкики, ищем минимальную сумму СКО*MAX значение датчика
    for i in range(1, len(valueList[0]) - times):
        sko = 0
        for value in valueList:
            if len(value)>(i + times):
                maxVal = value[i:i + times].max()
                if maxVal:
                    sko += value[i:i + times].std()/maxVal
                else:
                    sko += value[i:i + times].std()
        if (sko < min_sko) or min_sko!=-1:
            min_sko = sko
            optimal_pos = i
    dtList = detector.get_date_list()
    return (dtList[optimal_pos], dtList[optimal_pos + times])
        
        