from models import Detector
from models import Indication


class MaDetector(Detector):
    '''
        Датчик со сглаживанием методом скользящего среднего
    '''
    def __init__(self, detect, koef_ma):
        '''
            detect - датчик, который необходимо сгладить
            koef_ma - количество точек для скользящего среднего
        '''

        newKks = '{}_ma_{}'.format(detect.get_kks(), koef_ma)
        newDesc = '{} with ma {}'.format(detect.get_name(), koef_ma)
        super().__init__(newKks)
        sumList = list()
        for i, d in enumerate(detect.get_indication_list()):
            if i < koef_ma:
                sumList.append(d.value)
            else:
                ind = Indication(d.dt, sum(sumList)/koef_ma, d.status)
                self.add_indication(ind)
                sumList[i % koef_ma] = d.value
