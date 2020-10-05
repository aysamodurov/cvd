import numpy as np

def get_optimal_time(detector, times = 60):
    '''
        Выбор времени для обработки
        с минимальной скорость и случайной погрешностью
        detector - датчик
        times - количество точек, которые необходимо выбрать
        return дата начала и окончания промежутка с оптимальными для данных временами
    '''
    valueList:np.ndarray = np.array(detector.get_value_list())
    if len(valueList)<times:
        print('Недостаточная выборка данных')
        return (None,None)
    optimal_pos = 0
    min_sko = valueList[:times].std()
    for i in range(1,len(valueList)-times):
        sko = valueList[i:i+times].std()
        if sko<min_sko:
            min_sko = sko 
            optimal_pos = i
    dtList = detector.get_date_list()
    return (dtList[optimal_pos],dtList[optimal_pos+times])