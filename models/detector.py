import copy


class Detector():
    '''Класс описывающий отдельный датчик
        kks - kks датчика
        indications - список из Indication(датаи время, значение, статус)
    '''

    def __init__(self, kks, description=''):
        '''KKS датчика, массив значений типа Indication'''
        self.kks = kks
        self.description = description
        self.indicationList = list()

    # GETTERS
    def get_kks(self):
        '''возвращает kks датчика'''
        return self.kks

    def get_description(self):
        '''возвращает описание датчика'''
        return self.description

    def get_indication_list(self):
        '''возвращает массив indications'''
        return self.indicationList

    def get_date_list(self):
        '''возвращает массив значений из даты и времени'''
        return [val.dt for val in self.indicationList]

    def get_value_list(self):
        '''возвращает массив значений показаний'''
        return [val.value for val in self.indicationList]

    def get_status_list(self):
        '''возвращает массив значений cтатуса'''
        return [val.status for val in self.indicationList]

    def get_start_date(self):
        '''возвращает дату и время начала данных'''
        return self.get_date_list()[0]

    def get_finish_date(self):
        '''возвращает дату и время окончания данных'''
        return self.get_date_list()[-1]
    # END GETERS

    def add_indication(self, indication):
        ''' добавить одно значение типа Indication
            предварительно проверив есть ли за данное время данные
        '''
        if not self.indicationList or indication.dt < self.indicationList[0].dt or indication.dt > self.indicationList[-1].dt:
            self.indicationList.append(indication)
        elif indication.dt not in self.get_date_list():
            self.indicationList.append(indication)

    def add_indication_list(self, indicationList):
        ''' добавить массив значений indicationList,
            каждый элемент типа Indication
        '''
        for indication in indicationList:
            self.add_indication(indication)

    def extend(self, detector2):
        '''добавление значений в список(объединние 2 списков с одинаковыми kks)'''
        if self.kks == detector2.kks:
            for newIndication in detector2.get_indication_list():
                self.add_indication(newIndication)
            self.indicationList.sort()

    def count(self):
        '''количество показаний'''
        return len(self.get_value_list())

    def __repr__(self):
        '''представление для печати'''
        str1 = '{}\t{}\t{}\n'.format(self.kks, self.description, '\t'.join(str(e) for e in self.indicationList))
        return str1

    def __lt__(self, other):
        '''сравнение 2 значений'''
        return self.kks < other.kks

    def copy(self):
        '''скопировать объект'''
        return copy.deepcopy(self)

    def copy_indication_list(self):
        ''' скопировать indicationList'''
        return copy.deepcopy(self.indicationList)
