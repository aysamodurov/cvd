from models.detector import Detector
from models.indication import Indication
from datetime import timedelta


class DetectorList(list):
    '''список из Detector'''
    
    def __init__(self):
        super().__init__()
        
    def insert(self, detector)->bool:
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
    
    def extend(self, detectorList2):
        '''расширить список self списком detectorList2'''
        for detector in detectorList2:
            allKks = set(self.get_all_kks())
            if detector.get_kks() in allKks:
                detect = self.get_detector_by_kks(detector.get_kks())
                detect.extend(detector)   
            else:
                self.append(detector)


    def get_detector(self, kks, startTime=None,finishTime=None)->Detector:
        '''возвращает значение с указанным kks за указанный промежуток времени
        если не введено значение starttime, то берется интервал с начала и до finishtime
        если не введено значение finishtime, то берется интервал с starttime и до конца'''
        res = Detector(kks)
        try:
            for detect in self:
                if detect.kks == kks:
                    res = Detector(kks,detect.get_description())
                    # проверяем дату и время выборки данных и в случае неправильного ввода берем все данные
                    minDate = detect.get_start_date()
                    maxDate = detect.get_finish_date()
                    isValidStartTime = startTime and startTime>minDate and startTime<maxDate
                    startTime = startTime if isValidStartTime else minDate
                    isValidFinishTime = finishTime and finishTime>startTime
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
        except:
            print('Дата введена некорректно!!!')
        return res
    
    def get_detectors(self, kkslist, starttime=None,finishtime=None):
        '''Возвращает показания по kks из kkslist за промежуток времени
        от startdate до finishdate'''
        res = DetectorList()
        for kks in kkslist:
            res.append(self.get_detector(kks, starttime,finishtime))
        return res
    
    def get_all_kks(self):
        '''возвращает список kks всех датчиков'''
        return [k.kks for k in self]
    
    def get_detector_by_kks(self,kks):
        '''получение датчика по kks'''
        for detector in self:
            if detector.kks == kks:
                return detector
        return None
    
    def count(self):
        return self.count()

if __name__ == '__main__':
    # подключение папок
    import os, sys
    sys.path.append(os.path.abspath('..'))
    print(os.path.abspath('..'))
    print('start test detector_list')
    from reader import Reader
    import datetime

    reader = Reader().get_file_reader(r'E:\Project\cvd\data\PTK-Z.rsa')
    detectorList = reader.read_file()
    startTime = datetime.datetime.fromisoformat('2020-01-30 18:21:00')
    finishTime = datetime.datetime.fromisoformat('2020-01-30 18:21:10')
    detect:Detector = detectorList.get_detector('10JEC10CP832XQ62', startTime=startTime, finishTime=finishTime)
    print(detect.get_value_list())
    detect.calc_statistic()
    # firstVal = detect.get_value_by_time(datetime.datetime.fromisoformat('2020-01-30 18:22:01'))
    # print(firstVal)