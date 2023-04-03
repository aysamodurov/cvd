from models import Detector
from datetime import timedelta
from models.indication import Indication
import copy


class DetectorList(list):
    '''список из Detector'''

    def __init__(self):
        super().__init__()

    def insert(self, detector) -> bool:
        '''расширить список self
        detector  - Detector
        '''
        allKks = self.get_all_kks()
        if detector.get_kks() in allKks:
            detect = self.get_detector_by_kks(detector.get_kks())
            detect.extend(detector)
            return False
        else:
            self.append(detector)
            return True

    def extend(self, detector_list2):
        '''расширить список self списком detector_list2'''
        for detector in detector_list2:
            allKks = set(self.get_all_kks())
            if detector.get_kks() in allKks:
                detect = self.get_detector_by_kks(detector.get_kks())
                detect.extend(detector)
            else:
                self.append(detector)

    def get_detector(self, kks, start_time=None, finish_time=None) -> Detector:
        '''
            Поиск датчика по kks за определенный промежуто времени
            если параметры времени не заданы, то возвращает за все время что есть
            данные заполняются ежесекундно
            к случае пропусков в данных заполняется предыдущим значением

        kks (str) : KKS
        start_time (datetime) :  Дата и время начала выборки показаний
        finishTime (datetime) : Дата и время окончания выборки показаний
        -------
        Detector - Копия датчика из общего списка
        '''
        detector = copy.deepcopy(self.get_detector_by_kks(kks))

        # проверяем дату и время выборки данных
        # и в случае неправильного ввода берем все данные
        min_date = detector.get_start_date()
        max_date = detector.get_finish_date()
        is_valid_start_time = start_time and start_time > min_date and start_time < max_date
        start_time = start_time if is_valid_start_time else min_date
        is_valid_finish_time = finish_time and finish_time >= start_time
        finish_time = finish_time if is_valid_finish_time else max_date

        indication_lst = list(filter(lambda x: x.dt >= start_time and x.dt <= finish_time, detector.get_indication_list()))
        detector.indication_list = indication_lst

        if not ((finish_time-start_time).seconds == len(indication_lst)-1):
            indication = detector.get_indication_by_time(start_time)
            if indication.dt != start_time:
                indication_lst.add_indication(Indication(start_time, indication.value, indication.status))
            delta = timedelta(seconds=1)
            start_time += delta
        return detector

    def get_detectors(self, kkslist, starttime=None, finishtime=None):
        '''Возвращает показания по kks из kkslist за промежуток времени
        от startdate до finishdate'''
        res = DetectorList()
        for kks in kkslist:
            res.append(self.get_detector(kks, starttime, finishtime))
        return res

    def get_all_kks(self):
        '''возвращает список kks всех датчиков'''
        return [k.kks for k in self]

    def get_detector_by_kks(self, kks):
        '''получение датчика по kks'''
        for detector in self:
            if detector.kks == kks:
                return detector
        return None

    def update_all_description(self):
        '''
        Обновить описание датчиков, загрузив из настроечного файла

        '''
        for detector in self:
            detector.load_description()
