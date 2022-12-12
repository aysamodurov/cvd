import numpy as np
from datetime import timedelta
import logging

log = logging.getLogger(__name__)


def get_optimal_detector_time(detector, times=60):
    '''
        Выбор времени для обработки
        с минимальной скоростью и случайной погрешностью
        detector - датчик
        times - количество точек, которые необходимо выбрать
        return дата начала и окончания промежутка с оптимальными для данных временами
    '''
    log.info(f'Выбор времени для обработки {detector.get_kks()}')
    valueList = np.array(detector.get_value_list())
    if len(valueList) <= times:
        log.warning('Недостаточная выборка данных')
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


def get_optimal_time(detectorList, startDate, finishDate, times=60):
    '''
    Выбор времени для обработки
    с минимальной скорость и случайной погрешностью
    detectorList - датчик
    startDate - время начала выборки данных
    finishDate - время окончания выборки данных
    times - количество точек, которые необходимо выбрать
    return дата начала и окончания промежутка с оптимальными для данных временами
    '''
    log.info('Выбор времени для обработки с минимальной скорость и случайной погрешностью для всех датчиков')
    if startDate > finishDate - timedelta(seconds=times):
        return None, None
    valueList = []
    for kks in detectorList.get_all_kks():
        detector = detectorList.get_detector(kks, startDate, finishDate)
        valueList.append(np.array(detector.get_value_list()))
    optimal_pos = 0
    min_sko = -1
    # поиск участка данных с минимальным СКО/maxValue
    # оцениваются все датчкики, ищем минимальную сумму СКО/maxValue значение датчика
    for i in range(1, len(valueList[0]) - times):
        sko = 0
        for value in valueList:
            if len(value) > (i + times):
                maxVal = value[i:i + times].max()
                if maxVal:
                    sko += value[i:i + times].std()/maxVal
                else:
                    sko += value[i:i + times].std()
        if (sko < min_sko) or min_sko == -1:
            min_sko = sko
            optimal_pos = i
    log.info(f'Стабильное состояние начинается с {startDate + timedelta(seconds=optimal_pos)}')
    return (startDate + timedelta(seconds=optimal_pos), startDate + timedelta(seconds=optimal_pos + times))
