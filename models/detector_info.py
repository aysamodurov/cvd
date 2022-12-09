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
import configparser
import logging
import re

log = logging.getLogger(__name__)

class DetectorsInfo:

    def __init__(self):
        super().__init__()
        self.all_info = []

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

        log.info(f'Считывание файла [{infofile_filepath}] с настроечной информацией о датчиках в кодировке {infofile_encoding}')

        with open(infofile_filepath, 'r', encoding=infofile_encoding) as infofile:
            # пропустить пеовую строку
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

    def get_info(self, kks):
        for info in self.all_info:
            if re.match(info['mask'], kks):
                return info
        return None

    def _get_filepath_from_setting(self):
        """
        Получение пути к файлу с описанием датчиков

        Returns:
            filepath(str): путь к файлу с описанием датчиков
            encoding (str): кодировка
        """
        config = configparser.ConfigParser()
        config.read('config/settings.ini')
        folderpath = config['detectorInfoFile']['folderpath']
        filename = config['detectorInfoFile']['filename']
        filepath = f'{folderpath}/{filename}'
        encoding = config['detectorInfoFile']['encoding']
        return filepath, encoding
    
