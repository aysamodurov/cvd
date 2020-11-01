'''
Класс для расчета статистических показателей для Detector
'''

class DetectorStat():
    '''
    Класс для расчета следующих статистических показателей для Detector:
    среднее значение
    СКО
    Погрешность
    '''
    def __init__(self):
        # время за которое расчитываются статистические показания
        self.startTime = None
        self.finishTime = None
        # среднее занчание
        self.aver = 0
        # СКО
        self.sko = 0
        # погрешность
        self.error = 0

    # расчет статистических данных
    def calculate(self, detector):
        pass
