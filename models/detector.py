import copy
import models.statistic_utils as statUtils


class Detector():
    '''
        Класс описывающий отдельный датчик
        kks - kks датчика
        indications - список из Indication(датаи время, значение, статус)
    '''

    def __init__(self, kks, description=''):
        '''
            KKS датчика, массив значений типа Indication,
            mean - среднее значение
            sko - СКО
            error - СКО * Коэффициент Стьюдента
        '''
        self.kks = kks
        self.description = description
        self.indication_list = list()
        self.mean = 0
        self.sko = 0
        self.error = 0

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

    def get_value_by_time(self, dt):
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

    def calc_statistic(self):
        print('Calculation statistic for detector ', self.get_kks())
        values = self.get_value_list()
        self.mean = statUtils.calcMNKMean(values)
        self.sko = statUtils.calcSKO(values, self.mean)
        self.error = statUtils.calcError(self.sko, len(values))

    # GETTERS
    def get_kks(self):
        '''возвращает kks датчика'''
        return self.kks

    def get_description(self):
        '''возвращает описание датчика'''
        return self.description

    def get_indication_list(self):
        '''возвращает массив indications'''
        return self.indication_list

    def get_date_list(self):
        '''возвращает массив значений из даты и времени'''
        return [val.dt for val in self.indication_list]

    def get_value_list(self):
        '''возвращает массив значений показаний'''
        return [val.value for val in self.indication_list]

    def get_status_list(self):
        ''' возвращает массив значений cтатуса'''
        return [val.status for val in self.indication_list]

    def get_start_date(self):
        '''возвращает дату и время начала данных'''
        return self.get_date_list()[0]

    def get_finish_date(self):
        '''возвращает дату и время окончания данных'''
        return self.get_date_list()[-1]

    def get_statistic(self):
        '''возвращает массив со статистикой'''
        self.calc_statistic()
        return {'mean': self.mean, 'sko': self.sko, 'error': self.error}
    # END GETERS
