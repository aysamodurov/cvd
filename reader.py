from models import Detector
from models import DetectorList
from models import Indication
import datetime
import os


def create_reader(file_name):
    """Фабричный метод для выбора Reader
        в зависимотси от файла
        RsaReader: Чтение rsa файлов
        SVBUReader: Чтение файлов с СВБУ в стандатном формате
        SVBUFixedReader: Чтение файлов с СВБУ с фиксированным шагом

    Args:
        file_name (str): путь к файлу

    Returns:
        Reader: объект для чтения файла с методом read_file
    """

    _, extension = os.path.splitext(file_name)
    #  RSA файл
    if extension == '.rsa':
        return RsaReader(file_name)
    # TXT файл(один из нескольких вариантов)
    elif extension == '.txt':
        # СВБУ с произвольным шагом и СВБУ с фиксировнным шагом
        with open(file_name, 'r', encoding='utf-8') as f:
            table_title = None
            for _ in range(0, 4):
                table_title = f.readline()
            second_data = f.readline()
            second_data = f.readline()
            if (table_title.strip() == 'Время\tKKS\tЗнач\tЕд.изм\tДост\tОписание'):
                if (second_data[0] != '\t'):
                    return SVBUReader(file_name)
                else:
                    return SVBUFixedReader(file_name)


class Reader():
    """
    Класс родитель для всех Reader
    Применение - чтение информации из файлов с данными
    и сохранение в DetectorList в методе read_file
    """

    def __init__(self, file_name: str):
        super().__init__()
        self.file_name = file_name

    def read_file(self):
        """
        Общий для всех наследников метод
        который будет реализован в каждом классе
        
        Returns:
            DetectorList: список из Detector
        """
        if os.path.exists(self.file_name):
            self.file_exist = True
            print('Start read', type(self))
        else:
            self.file_exist = False
        return DetectorList()


class RsaReader(Reader):
    """Реалищация Reader класса для считывания инфомации из RSA файлов"""

    def read_file(self):
        """чтение из rsa файла

        Returns:
            DetectorList: список из Detector 
            или None если файл не существует
        """
        super().read_file()
        if not self.file_exist:
            return None
        detector_list = DetectorList()
        with open(self.file_name, 'r', encoding='koi8-r') as rsafile:
            for line in rsafile:
                # если в файле найдена строка с KKS выделить KKS
                # и заполнить detector_list KKS и пустым списком с Indication
                if line.find('SignalsArray=') != -1:
                    line = line[line.find('=') + 1:-2]
                    kkslist = line.split(';')
                    # добавить новый элемент в список с датчиками
                    for kks in kkslist:
                        detector_list.insert(Detector(kks))
                # если в файле найдена строка с данными
                elif line.find('RsaData=') != -1:
                    # удаляем из начала строки "RsaData="
                    line = line[line.find('=') + 1:-2]
                    indications = line.split(';')
                    # получаем дату и время из строки и удаляем из массива
                    try:
                        date = datetime.datetime.strptime(indications.pop(0), '%d.%m.%Y %H:%M:%S.%f').replace(microsecond=0)
                        # удалить первое число у первого датчика
                        # у первого датчика 4 значение, первое из которых относится ко всей строке
                        indications[0] = indications[0][indications[0].find(' ') + 1:]
                        for value in indications:
                                pos, val, status = value.split(' ')
                                indication = Indication(date, float(val), int(status))
                                detector_list[int(pos) - 1].add_indication(indication)
                    except ValueError:
                        continue

        for detector in detector_list:
            detector.indicationList.sort()
        return detector_list


class SVBUReader(Reader):
    """Реалищация Reader класса для считывания инфомации из 
    СВБУ файлов в стандартном формате"""

    def read_file(self):
        super().read_file()
        if not self.file_exist:
            return None
        detector_list = DetectorList()
        with open(self.file_name, encoding='utf-8') as file:
            for line in file:
                values = line.split('\t')
                # проверка, если строка начинается с числа(даты), то это строка с данными
                if (values[0].split('.')[0]).isdigit():
                    try:
                        dt = datetime.datetime.strptime(values[0], '%d.%m.%y %H:%M:%S,%f').replace(microsecond=0)
                        kks = values[1]
                        value = 0
                        status = 7
                        if is_float(values[2]):
                            value = float(values[2])
                            # проверка на достоверность: 7- недостоверно, 0 - достоверно
                            if values[4] == 'дост':
                                status = 0
                        desc = values[5]
                        # добавление нового датчика
                        detect = Detector(kks, desc)
                        indication = Indication(dt, value, status)
                        detect.add_indication(indication)
                        detector_list.insert(detect)
                    except ValueError:
                        continue
        return detector_list


class SVBUFixedReader():
    """Реалищация Reader класса для считывания инфомации из 
    СВБУ файлов с фиксированным шагом"""

    def read_file(self):
        super().read_file()
        if not self.file_exist:
            return None
        detector_list = DetectorList()
        with open(self.file_name, encoding='utf-8') as file:
            for line in file:
                values = line.split('\t')
                # Проверка, если строка начинается с даты,
                # то это строка с данными
                if (values[0].split('.')[0]).isdigit():
                    dt = datetime.datetime.strptime(values[0], '%d.%m.%y %H:%M:%S')
#                 считываем значения
                if (values[0] == ''):4
                try:
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
                    detector_list.insert(detect)
                except ValueError:
                    continue
        return detector_list


def is_float(val):
    """Проверка является ли строка числом

    Args:
        val (str): строка для проверки

    Returns:
        bool: ответ
    """
    try:
        float(val)
        return True
    except ValueError:
        return False
