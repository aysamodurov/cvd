from detector_list import DetectorList

from reader import create_reader
import calculations


class DetectorController():

    def __init__(self):
        # список датчиков
        self.allDetectors = DetectorList()
        # файлы из которых считаны данные
        self.readedFiles = list()
        # время начала и окончания для выборки из данных
        self.startDate = None
        self.finishDate = None
        # границы для времени за которые есть данные
        self.maxDate = None
        self.minDate = None
        # выбранный детектор
        self.currentDetector = None
        self.minOptimalTime = None
        self.maxOptimalTime = None

    def loading_data(self, filesNames, isNewList=False):
        '''загрузка файлов
            filesName - имена файлов, которые необходимо загрузить
            isNewList - признак создания нового списка(удаление старых данных)
        '''
        # очистка данных в случае создания нового списка
        print('START LOAD')
        isNewList = isNewList or not self.readedFiles
        if isNewList:
            self.allDetectors.clear()
            self.currentDetector = None
            self.readedFiles.clear()
#         загрузка данных из файлов
        for fileName in filesNames:
            self.readedFiles.append(fileName)
            reader = create_reader(fileName)
            if not reader:
                print('Файл не найден')
                return
            self.allDetectors.extend(reader.read_file())
        # выбор текущего детектора
        if self.allDetectors:
            self.currentDetector = self.allDetectors[0]
        self.update_current_min_max_date()
        if isNewList:
            self.reset_start_finish_date()

    def update_current_detector(self, kks=''):
        '''Изменить текущий детектор на новый по kks,
        если за заданный промежуток нет данных, то сбросить время - ok'''
        print('update_current_detector')
        if kks == '':
            kks = self.currentDetector.get_kks()
        self.currentDetector = self.allDetectors.get_detector(kks)
        detect = self.allDetectors.get_detector(kks, self.startDate, self.finishDate)
        self.update_current_min_max_date()
        if detect.get_indication_list():
            self.currentDetector = detect
        else:
            self.reset_start_finish_date()
        # выбор оптимального времени
        self.minOptimalTime, self.maxOptimalTime = calculations.get_optimal_detector_time(self.currentDetector)
        print('OPTIMAL ', self.minOptimalTime, self.maxOptimalTime)
        #Обновить дату и время
        self.update_date(self.currentDetector.get_start_date(),self.currentDetector.get_finish_date())


    def update_current_min_max_date(self):
        print('update_current_min_max_date')
        if self.currentDetector:
            self.minDate = self.currentDetector.get_start_date()
            self.maxDate = self.currentDetector.get_finish_date()
        else:
            self.minDate = None
            self.maxDate = None

    # сброс времени и даты в экземпляре класса
    def reset_start_finish_date(self):
        print('reset_start_finish_date')
        self.startDate = self.minDate
        self.finishDate = self.maxDate
        self.minOptimalTime, self.maxOptimalTime = calculations.get_optimal_detector_time(self.currentDetector)

    #обновление даты в экземпляре класса
    def update_date(self, startDate, finishDate):
        print('update_date')
        self.startDate = startDate
        self.finishDate = finishDate

    #автоматический выбор оптимального времени  для расчета
    def get_optimal_time(self):
        return calculations.get_optimal_time(self.allDetectors, self.startDate, self.finishDate)

    # получить таблицу, каждаю строка состоит из KKS, статистика
    # статистика : {'mean' : self.mean, 'sko' : self.sko, 'error': self.error}
    def get_stats(self):
        print('get stats')
        res = []
        for kks in self.allDetectors.get_all_kks():
            detect = self.allDetectors.get_detector(kks,self.startDate,self.finishDate)
            res.append([detect.get_kks(), detect.get_statistic()])
        return res