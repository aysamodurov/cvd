import copy
import models.statistic_utils as statUtils
from models.detectors_info import DetectorsInfo


class Detector():
    '''
        Класс описывающий отдельный датчик
        kks - kks датчика
        indications - список из Indication(датаи время, значение, статус)
    '''
    detectors_info = DetectorsInfo()

    def __init__(self, kks, descr = '', munit = ''):
        '''
            KKS датчика, массив значений типа Indication,
            description: описание, загруженное из файла из диагностики
            mean - среднее значение
            sko - СКО
            error - СКО * Коэффициент Стьюдента
        '''
        self.kks = kks
        self.description = {}
        self.load_description(descr, munit)
        self.indication_list = list()
        
    def add_indication(self, indication):
        ''' добавить одно значение типа Indication
            предварительно проверив есть ли за данное время данные
        '''
        if not self.indication_list or indication.dt < self.indication_list[0].dt \
                or indication.dt > self.indication_list[-1].dt:
            self.indication_list.append(indication)
        elif indication.dt not in self.get_date_list():
            self.indication_list.append(indication)

    def add_indication_list(self, indication_list):
        ''' добавить массив значений indication_list,
            каждый элемент типа Indication
        '''
        for indication in indication_list:
            self.add_indication(indication)
        self.sort_indication_list()

    def extend(self, detector2):
        """добавление значений в список
        (объединние 2 списков с одинаковыми kks)"""
        if self.kks == detector2.kks:
            for newIndication in detector2.get_indication_list():
                self.add_indication(newIndication)
            self.sort_indication_list()
    
    def load_description(self, descr='', munit=''):
        '''
            Загрузить описание из DetectorsInfo
        '''
        self.description = self.detectors_info.get_info(self.kks)
        if self.description['name']  == '' and descr:
            self.description['name'] = descr
        if self.description['munit']  == '' and munit:
            self.description['munit'] = munit

    def sort_indication_list(self, reverse=False):
        """Сортировка массива с показаниями Indication

        Args:
            reverse (bool, optional):
            Сортировка по возрастанию или убыванию (по умолчанию по возрастанию).
        """
        self.indication_list.sort(reverse=reverse)

    def count(self):
        '''количество показаний'''
        return len(self.indication_list)

    def __repr__(self):
        '''представление для печати'''
        str1 = '{}\t{}\t{}\n'.format(self.kks, self.description, '\t'.join(str(e) for e in self.indication_list))
        return str1

    def __lt__(self, other):
        '''сравнение 2 значений'''
        return self.kks < other.kks
    
    def copy(self):
        '''скопировать объект'''
        return copy.deepcopy(self)

    def copy_indication_list(self):
        ''' скопировать indication_list'''
        return copy.deepcopy(self.indication_list)

    def get_indication_by_time(self, dt):
        '''получить значение во время dt
        или ближайшее которое было до него
        Return:
            Indication значение'''
        if self.indication_list[0].dt > dt:
            return self.indication_list[0]
        for val in self.indication_list:
            if val.dt >= dt:
                return val
        return self.indication_list[-1]
    
    def calculate_statistic(self):
        '''
        возвращает массив со статистикой
        Result:
            'mean': Среднее значение
            'sko': СКО
            'error': погрешность
            'outliers_percent': процент выбросов
            'rate_of_change': скорость изменения параметра
        '''
        values = self.get_value_list()
        mean = statUtils.calcMNKMean(values)
        sko = statUtils.calcSKO(values, mean)
        error = statUtils.calcError(sko, len(values))
        outliers_percent = statUtils.calc_outliers(self.get_value_list(), self.description['delta'], mean)
        rate_of_change = statUtils.calc_rate_of_change(values)
        
        return {
                'mean': mean,
                'sko': sko,
                'error': error,
                'outliers_percent': outliers_percent,
                'rate_of_change': rate_of_change
            }

    # GETTERS
    def get_kks(self):
        '''возвращает kks датчика'''
        return self.kks

    def get_name(self):
        '''возвращает описание датчика'''
        if self.description['name']:
            return self.description['name']
        return ''
    
    def get_munit(self):
        '''возвращает описание датчика'''
        if self.description['munit']:
            return self.description['munit']
        return ''

    def get_indication_list(self):
        '''возвращает массив indications'''
        return self.indication_list

    def get_date_list(self):
        '''возвращает массив значений из даты и времени'''
        return [val.dt for val in self.indication_list]

    def get_value_list(self):
        '''возвращает массив значений показаний'''
        return [val.value for val in self.indication_list]
    
    def get_true_value_list(self):
        '''возвращает массив достоверных занчений значений показаний'''
        return [val.value for val in self.indication_list if val.status != 7]

    def get_status_list(self):
        ''' возвращает массив значений cтатуса'''
        return [val.status for val in self.indication_list]

    def get_start_date(self):
        '''возвращает дату и время начала данных'''
        return self.get_date_list()[0]

    def get_finish_date(self):
        '''возвращает дату и время окончания данных'''
        return self.get_date_list()[-1]
    
    def get_delta(self):
        '''возвращает допустимую погрешность'''
        if 'delta' in self.description:
            return self.description['delta']
        else:
            return 0
    # END GETERS
