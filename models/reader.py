from models import Detector
from models import DetectorList
from models import Indication
from models.utils import timer
import datetime
import os
import logging

log = logging.getLogger(__name__)


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
    log.info('Создание FileReader')
    _, extension = os.path.splitext(file_name)
    #  RSA файл
    if extension == '.rsa':
        log.info('Создание RSAReader')
        return RsaReader(file_name, 'koi8-r')
    # TXT файл(один из нескольких вариантов)
    elif extension == '.txt':
        # СВБУ с произвольным шагом и СВБУ с фиксировнным шагом
        encodings = ['utf-8', 'windows-1251', 'koi8-r']
        for encode in encodings:
            print(encode)
            try:
                with open(file_name, 'r', encoding=encode) as f:
                    table_title = None
                    for _ in range(0, 4):
                        table_title = f.readline()
                    second_data = f.readline()
                    second_data = f.readline()
                    if table_title.strip() == 'Время\tKKS\tЗнач\tЕд.изм\tДост\tОписание':
                        if second_data[0] != '\t':
                            log.info('Создание SVBUFReader')
                            return SVBUReader(file_name, encode)
                        else:
                            log.info('Создание SVBUFixedReader')
                            return SVBUFixedReader(file_name, encode)
                    else:
                        date = ' '.join(table_title.strip().split()[:2])
                        try:
                            datetime.datetime.strptime(date, '%d.%m.%Y %H:%M:%S.%f')
                            log.info('Создание TxtReader')
                            return TxtReader(file_name, encode)
                        except Exception:
                            log.info('Это не TxtReader')
            except UnicodeDecodeError:
                log.warning('Кодировка {} не подошла для файла {}'.format(encode, file_name))
                print('Кодировка {} не подошла для файла {}'.format(encode, file_name))


class Reader:
    """
    Класс родитель для всех Reader
    Применение - чтение информации из файлов с данными
    и сохранение в DetectorList в методе read_file
    """

    def __init__(self, file_name: str, encode: str):
        super().__init__()
        self.file_name = file_name
        self.encode = encode

    def read_file(self):
        """
        Общий для всех наследников метод
        который будет реализован в каждом классе
        
        Returns:
            DetectorList: список из Detector
        """
        if os.path.exists(self.file_name):
            self.file_exist = True
        else:
            self.file_exist = False
        return DetectorList()


class RsaReader(Reader):
    """Реалищация Reader класса для считывания инфомации из RSA файлов"""

    @timer
    def read_file(self):
        """чтение из rsa файла

        Returns:
            DetectorList: список из Detector
            или None если файл не существует
        """
        log.info(f'Чтение RSA файла : {self.file_name}')
        
        super().read_file()
        if not self.file_exist:
            log.warning(f'Файл {self.file_name} не найден')
            return None
        
        detector_list = DetectorList()
        with open(self.file_name, 'r', encoding=self.encode) as rsafile:
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
                            position, val, status = value.split(' ')
                            indication = Indication(date, float(val), int(status))
                            detector_list[int(position) - 1].add_indication(indication)
                    except ValueError:
                        log.warning(f'Некорректный формат строки : {line}')

        for detector in detector_list:
            detector.indication_list.sort()
        log.info('RSA файл прочитан')
        return detector_list


class SVBUReader(Reader):
    """
        Реалищация Reader класса для считывания инфомации из
        СВБУ файлов в стандартном формате
    """

    @timer
    def read_file(self):
        log.info(f'Чтение СВБУ файла : {self.file_name}')
        
        super().read_file()
        if not self.file_exist:
            log.warning(f'Файл {self.file_name} не найден')
            return None
        
        detector_list = DetectorList()
        with open(self.file_name, encoding=self.encode) as file:
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
                        log.warning(f'Некорректный формат строки: {line}')
        log.info('СВБУ файл прочитан')
        return detector_list


class SVBUFixedReader(Reader):
    """
        Реализация Reader класса для считывания инфомации из
        СВБУ файлов с фиксированным шагом
    """

    @timer
    def read_file(self):
        log.info(f'Чтение СВБУ файла с фиксированным шагом : {self.file_name}')
        
        super().read_file()
        
        if not self.file_exist:
            log.warning(f'Файл {self.file_name} не найден')
            return None
       
        detector_list = DetectorList()
        with open(self.file_name, encoding=self.encode) as file:
            
            for line in file:
                values = line.split('\t')
                # Проверка, если строка начинается с даты,
                # то это строка с данными
                if (values[0].split('.')[0]).isdigit():
                    dt = datetime.datetime.strptime(values[0], '%d.%m.%y %H:%M:%S')
                    values[0] = ''
#                 считываем значения
                if values[0] == '':
                    try:
                        kks = values[1]
                        
                        value = 0
                        if is_float(values[2]):
                            value = float(values[2])
                        
                        # проверка на достоверность 7 - недост, 0 - дост
                        status = 7
                        if values[4] == 'дост':
                            status = 0
                            
                        desc = values[5]
                        munit = values[3]
    #                     добавление нового датчика
                        detect = Detector(kks, desc, munit)
                        indication = Indication(dt, value, status)
                        detect.add_indication(indication)
                        detector_list.insert(detect)
                    except ValueError:
                        log.warning(f'Некорректный формат строки: {line}')
                        continue
        log.info('СВБУ файл с фиксированным шагом прочитан')
        return detector_list


class TxtReader(Reader):
    """
    Реализация Reader класса для считывания инфомации из
    txt файлов вида
    1. KKS
    2. Название
    3. Дата время данные
    """

    @timer
    def read_file(self):
        log.info(f'Чтение простого файла текстового формата  : {self.file_name}')
        super().read_file()

        if not self.file_exist:
            log.warning(f'Файл {self.file_name} не найден')
            return None

        detector_list = DetectorList()
        with open(self.file_name, encoding=self.encode) as file:
            # строка с KKS
            kks_list = file.readline().split('\t')
            # строка с названиями
            description_list = file.readline().split('\t')
            if len(kks_list) != len(description_list):
                log.error('Количество KKS и описаний в файле не совпадает')
                description_list.extend(['']*(len(kks_list)-len(description_list)))
            for kks, description in zip(kks_list, description_list):
                detector_list.insert(Detector(kks, descr=description))


            # чтение показаний
            for line in file:
                # если встретилась непустая строка с показаниями
                if line.strip():
                    values = line.strip().split('\t')
                    date = datetime.datetime.strptime(values.pop(0), '%d.%m.%Y %H:%M:%S.%f').replace(microsecond=0)
                    for index, value in enumerate(values):
                        if is_float(value):
                            indication = Indication(date, float(value), 0)
                            detector_list[index].add_indication(indication)
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
