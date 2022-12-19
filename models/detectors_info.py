"""
Модуль для работы с настроечным файлом с описанием датчиков из Dynamic
Файл содержит столбцы, разделенные табуляцией
    KKS (Mask KKS) - маска KKS или сам KKS
    Delta - допустимая погрешность датчиков
    Name - название датчиков
    Munit - еденица измерения
    Discrete(NULL or any_value) - признак дискретности сигнала
    если значение отсутствует значит False
    SystematicError - систематическая погрешность
"""
import re
import config
from models.utils import singleton
import logging

log = logging.getLogger(__name__)


@singleton
class DetectorsInfo:
    """
    Класс для рабботы с настроечным файлом с информацией о датчиках
    Содержит :
    метод для чтения настроечной информации и сохраниния ее в all_info
    в виде словарей
    {
        mask - маска или KKS
        delta - допустимая погрешность датчиков
        name - название датчиков
        munit - еденица измерения
        discrete - признак дискретности сигнала
        systematic_error - систематическая погрешность
    }
    метод для поиска в словаре по kks
    """

    def __init__(self):
        log.info('Инициализация DetectorsInfo')
        super().__init__()
        self.all_info = []
        self.load_from_file()

    def load_from_file(self):
        """
            Чтение информации из настроечного файла
            и сохранение в массив из слованей с полями
            {
                mask - маска или KKS
                delta - допустимая погрешность датчиков
                name - название датчиков
                munit - еденица измерения
                discrete - признак дискретности сигнала
                systematic_error - систематическая погрешность
            }
        """
        infofile_filepath, infofile_encoding = self._get_filepath_from_setting()
        self.all_info = []

        log.info(f'Считывание файла [{infofile_filepath}] с настроечной информацией о датчиках в кодировке {infofile_encoding}')

        try:
            with open(infofile_filepath, 'r', encoding=infofile_encoding) as infofile:
                # пропустить первую строку
                infofile.readline()
                for line in infofile:
                    line = line.strip()
                    if line:
                        detector_info = line.split('\t')
                        # добавить пустые столбцы если они отсутствуют
                        detector_info.extend([''] * (6 - len(detector_info)))
                        keys = ['mask', 'delta', 'name', 'munit', 'discrete', 'systematic_error']
                        detector_info_dict = dict(zip(keys, detector_info))
                        # преобразование строк к необходимым типам
                        try:
                            detector_info_dict['mask'] = detector_info_dict['mask'].replace('*', '.*').replace('?', '\w')
                            detector_info_dict['delta'] = float(detector_info_dict['delta'])
                            detector_info_dict['discrete'] = detector_info_dict['delta'] != ''
                            if detector_info_dict['systematic_error']:
                                detector_info_dict['systematic_error'] = float(detector_info_dict['systematic_error'])
                            else:
                                detector_info_dict['systematic_error'] = 0
                        except ValueError:
                            log.warning(f'Данная строка не является настроечной: [{line}]')

                        self.all_info.append(detector_info_dict)
            log.info(f'Завершено считывание файла [{infofile_filepath}] с настроечной информацией о датчиках в кодировке {infofile_encoding}')
        except FileNotFoundError:
            log.warning(f'Файл {infofile_filepath} не найден!!!')

    def get_info(self, kks):
        """Поиск информации по kks

        Args:
            kks (str): KKS датчика

        Returns:
            dict: {
                mask - маска или KKS
                delta - допустимая погрешность датчиков
                name - название датчиков
                munit - еденица измерения
                discrete - признак дискретности сигнала
                systematic_error - систематическая погрешность
            }
        информация о датчике
        """
        for info in self.all_info:
            if re.match(info['mask'], kks):
                return info
        return {
                'mask': '',
                'delta': 0,
                'name': '',
                'munit': '',
                'discrete': 0,
                'systematic_error': 0
            }

    def _get_filepath_from_setting(self):
        """
        Получение пути к файлу с описанием датчиков

        Returns:
            filepath(str): путь к файлу с описанием датчиков
            encoding (str): кодировка
        """

        folderpath = config.read_value('detectorInfoFile', 'folderpath')
        filename = config.read_value('detectorInfoFile', 'filename')
        filepath = f'{folderpath}/{filename}'
        encoding = config.read_value('detectorInfoFile', 'encoding', 'utf-8')
        return filepath, encoding
