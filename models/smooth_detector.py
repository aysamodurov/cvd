from models import Detector
from models import Indication


class SmoothDetector(Detector):
    '''
        Датчик со сглаживанием
    '''
    def __init__(self, detect, koef):
        '''
            detect - датчик, который необходимо сгладить
            koef_smoothing - коэффициент сглаживания
        '''
        newKks = '{}_smooth_{}'.format(detect.get_kks(), koef)
        newDesc = '{}_with smooth_{}'.format(detect.get_description(), koef)
        super().__init__(newKks, newDesc)
        valPr = detect.indicationList[0].value
        for indication in detect.indicationList:
            valPr = valPr + (indication.value-valPr)*koef
            newIndication = Indication(indication.dt, valPr, indication.status)
            self.add_indication(newIndication)
