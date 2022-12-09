from models import DetectorList

from models import Reader, create_reader
import calc_optimal_time
import app_logger
log = app_logger.get_logger(__name__)
        
class DetectorController():

    def __init__(self):
        log.info('Create detector controller')
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
        log.info('Начало загрузки данных в DetectorController')
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
                log.warning('Файл не найден')
                return
            self.allDetectors.extend(reader.read_file())
        # выбор текущего детектора
        if self.allDetectors:
            self.currentDetector = self.allDetectors[0]
        self.update_current_min_max_date()
        if isNewList:
            self.reset_start_finish_date()
        log.info('В DetectorController загружены данные')

    def update_current_detector(self, kks=''):
        '''Изменить текущий детектор на новый по kks,
        если за заданный промежуток нет данных, то сбросить время - ok'''
        log.info(f'Обновление текущего датчика на {kks}')
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
        self.minOptimalTime, self.maxOptimalTime = calc_optimal_time.get_optimal_detector_time(self.currentDetector)
        # Обновить дату и время
        self.update_date(self.currentDetector.get_start_date(), self.currentDetector.get_finish_date())

    def update_current_min_max_date(self):
        """
            Обновить время выбранного интервала
        """
        log.info(f'Обновление времени начала данных и окончания для датчика {self.currentDetector.get_kks()}')
        if self.currentDetector:
            self.minDate = self.currentDetector.get_start_date()
            self.maxDate = self.currentDetector.get_finish_date()
        else:
            self.minDate = None
            self.maxDate = None

    # сброс времени и даты в экземпляре класса
    def reset_start_finish_date(self):
        log.info(f'Сбросить дату вырезки данных на весь период')
        self.startDate = self.minDate
        self.finishDate = self.maxDate
        self.minOptimalTime, self.maxOptimalTime = calc_optimal_time.get_optimal_detector_time(self.currentDetector)

    # обновление даты в экземпляре класса
    def update_date(self, startDate, finishDate):
        log.info(f'Обновить дату вырезки данных на {startDate} - {finishDate}')
        self.startDate = startDate
        self.finishDate = finishDate

    # автоматический выбор оптимального времени  для расчета
    def get_optimal_time(self):
        return calc_optimal_time.get_optimal_time(self.allDetectors, self.startDate, self.finishDate)

    # получить таблицу, каждаю строка состоит из KKS, статистика
    # статистика : {'mean' : self.mean, 'sko' : self.sko, 'error': self.error}
    def get_stats(self):
        log.info(f'Получение статистических данных для всех датчиков')
        res = []
        for kks in self.allDetectors.get_all_kks():
            detect = self.allDetectors.get_detector(kks, self.startDate, self.finishDate)
            res.append([detect.get_kks(), detect.get_statistic()])
        return res

    def get_current_detector(self):
        """Вернуть текущий датчик

        Returns:
            Detector: выделенный датчик
        """
        return self.currentDetector

    def get_detectors(self):
        """Вернуть список всех датчиков

        Returns:
            DetectorList: список всех датчиков
        """
        return self.allDetectors

    def get_detector_by_kks(self, kks):
        """Вернуть датчик с заданным kks

        Args:
            kks (str): kks
        Returns:
            Detector: датчик с kks
        """
        return self.allDetectors.get_detector_by_kks(kks)

    def add_new_detector(self, detector):
        """добавить новый датчик в allDetectors

        Args:
            detector (Detector): новый датчик
        """
        self.allDetectors.insert(detector)

    def get_all_kks(self):
        """Вернуть список из kks

        Returns:
            list(str): Список kks всех датчиков
        """
        return self.allDetectors.get_all_kks()
