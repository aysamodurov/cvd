from models import Detector
from models.indication import Indication
from datetime import timedelta


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

    def get_detector(self, kks, startTime=None, finishTime=None) -> Detector:
        '''возвращает значение с указанным kks за указанный промежуток времени
        если не введено значение starttime,
        то берется интервал с начала и до finishtime
        если не введено значение finishtime,
        то берется интервал с starttime и до конца'''
        res = Detector(kks)

        for detect in self:
            if detect.kks == kks:
                res = Detector(kks, detect.get_description())
                # проверяем дату и время выборки данных
                # и в случае неправильного ввода берем все данные
                minDate = detect.get_start_date()
                maxDate = detect.get_finish_date()
                isValidStartTime = startTime and startTime > minDate and startTime < maxDate
                startTime = startTime if isValidStartTime else minDate
                isValidFinishTime = finishTime and finishTime >= startTime
                finishTime = finishTime if isValidFinishTime else maxDate
                # выбор среза данных по времени
                values = [val for val in detect.copy_indication_list()
                          if (val.dt >= startTime) & (val.dt <= finishTime)]
                # данные за каждую секунду
                if ((finishTime-startTime).seconds == len(values)-1):
                    res.add_indication_list(values)
                # данные с пропусками (не каждую секунду)
                else:
                    # первое значение
                    val = detect.get_value_by_time(startTime)
                    res.add_indication(Indication(startTime, val.value, val.status))
                    delta = timedelta(seconds=1)
                    startTime += delta
                    dates = set(val.dt for val in values)
                    while startTime <= finishTime:
                        if startTime in dates:
                            val = detect.get_value_by_time(startTime)
                        else:
                            val = Indication(startTime, val.value, val.status)
                        res.add_indication(val)
                        startTime += delta
                break

        return res

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
