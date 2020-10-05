from detector import Detector
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
    
    
    def get_detector(self, kks, starttime=None,finishtime=None)->Detector:
        
        '''возвращает значение с указанным kks за указанный промежуток времени
        если не введено значение starttime, то берется интервал с начала и до finishtime
        если не введено значение finishtime, то берется интервал с starttime и до конца'''
        res = Detector(kks)
        try:
            for detect in self:
                if detect.kks == kks:
                    res = Detector(kks,detect.get_description())
    #                 выбор среза данных по времени
                    if starttime and finishtime and (starttime<finishtime):
                        res.add_indication_list([val for val in detect.copy_indication_list() if (val.dt>=starttime)&(val.dt<=finishtime)])
                    elif starttime and not finishtime:
                        res.add_indication_list([val for val in detect.copy_indication_list() if (val.dt>=starttime)])
                    elif not starttime and finishtime:
                        res.add_indication_list([val for val in detect.copy_indication_list() if (val.dt<=finishtime)])
                    elif not starttime and not finishtime:
                        res.add_indication_list([val for val in detect.copy_indication_list()])
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