from detector import Detector
from detector_list import DetectorList
from indication import Indication
import datetime
import os


class Reader():

    def get_file_reader(self, fileName):
        '''Выбор нужного Reader в зависимости от файла,
         fileName путь к файлу'''
        try:
            #  RSA файл
            _, extension = os.path.splitext(fileName)
            if extension == '.rsa':
                return RsaReader(fileName)
            # TXT файл(один из нескольких вариантов)
            elif extension == '.txt':
                # СВБУ с произвольным шагом и СВБУ с фиксировнным шагом
                with open(fileName, 'r', encoding='utf-8') as f:
                    tableTitle = None
                    for _ in range(0, 4):
                        tableTitle = f.readline()
                    second_data = f.readline()
                    second_data = f.readline()
                    if (tableTitle.strip() == 'Время\tKKS\tЗнач\tЕд.изм\tДост\tОписание'):
                        if (second_data[0] != '\t'):
                            return SVBUReader(fileName)
                        else:
                            return SVBUFixedReader(fileName)
            return None
        except:
            return None


class RsaReader():
    '''Реалищация класса для считывания инфомации из RSA файлов'''

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName

    def read_file(self):
        '''чтение из rsa файлов
        files_name - массив из списка с названиями файлов
        возвращает список из Indication'''
        detectorList = DetectorList()
        try:
            f = open(self.fileName, 'r')
            for line in f:
                # если в файле найдена строка с KKS выделить KKS
                # и заполнить detector_list KKS и пустым списком со значениями
                if line.find('SignalsArray=') != -1:
                    line = line[line.find('=') + 1:-2]
                    kkslist = line.split(';')
                    # добавить новый элемент в список с датчиками
                    for kks in kkslist:
                        detectorList.insert(Detector(kks))
                # если в файле найдена строка с данными
                elif line.find('RsaData=') != -1:
                    # удаляем из начала строки "RsaData="
                    line = line[line.find('=') + 1:-2]
                    indications = line.split(';')
                    # получаем дату и время из строки и удаляем из массива
                    date = datetime.datetime.strptime(indications.pop(0), '%d.%m.%Y %H:%M:%S.%f').replace(microsecond=0)
                    # удалить первое число у первого датчика
                    # у первого датчика 4 значение, первое из которых относится ко всей строке
                    indications[0] = indications[0][indications[0].find(' ') + 1:]
                    for value in indications:
                        pos, val, status = value.split(' ')
                        indication = Indication(date, float(val), int(status))
                        detectorList[int(pos) - 1].add_indication(indication)
            f.close()
        except:
            print('\033[31m Файл {} не найден \033[0m'.format(self.fileName))
#             сортировка показаний по времени
        for detector1 in detectorList:
            detector1.indicationList.sort()
        return detectorList


class SVBUReader():
    '''Реализация класса для считывания инфомации
    из СВБУ файлов с произвольным шагом'''

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName

    def read_file(self):
        detectorList = DetectorList()
        with open(self.fileName, encoding='utf-8') as file:
            for line in file:
                values = line.split('\t')
                # проверка, если строка начинается с числа(даты), то это строка с данными
                if (values[0].split('.')[0]).isdigit():
                    dt = datetime.datetime.strptime(values[0], '%d.%m.%y %H:%M:%S,%f').replace(microsecond=0)
                    kks = values[1]
                    value = 0
                    status = 7
                    if is_float(values[2]):
                        value = float(values[2])
                        # проверка на достоверность: 7- недостоверно, 0 -достоверно
                        if values[4] == 'дост':
                            status = 0
                    desc = values[5]
                    # добавление нового датчика
                    detect = Detector(kks, desc)
                    indication = Indication(dt, value, status)
                    detect.add_indication(indication)
                    detectorList.insert(detect)
        return detectorList


class SVBUFixedReader():
    '''Реализация класса для считывания инфомации
     из СВБУ файлов с фиксированным шагом'''

    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName

    def read_file(self):
        print('SVBUReader read file')
        detectorList = DetectorList()
        with open(self.fileName, encoding='utf-8') as file:
            for line in file:
                values = line.split('\t')
                # Проверка, если строка начинается с даты,
                # то это строка с данными
                if (values[0].split('.')[0]).isdigit():
                    dt = datetime.datetime.strptime(values[0], '%d.%m.%y %H:%M:%S')
#                 считываем значения
                if (values[0] == ''):
                    kks = values[1]
                    value = 0
                    status = 7
                    if is_float(values[2]):
                        value = float(values[2])
#                     проверка на достоверность 7- недостоверно, 0 -достоверно
                        if values[4] == 'дост':
                            status = 0
                    desc = values[5]
#                     добавление нового датчика
                    detect = Detector(kks, desc)
                    indication = Indication(dt, value, status)
                    detect.add_indication(indication)
                    detectorList.insert(detect)
        return detectorList


def is_float(val):
    try:
        float(val)
        return True
    except:
        return False
