"""
    Модуль для работы с ini файлом
"""
import configparser
import os
import logging
log = logging.getLogger(__name__)


CONFIG_FILE_NAME = 'config/settings.ini'
config = configparser.ConfigParser()
# Если файл конфигурации не существует, то создаем новый
if not os.path.exists(CONFIG_FILE_NAME):
    print(f'Не найден файл конфигурации {CONFIG_FILE_NAME}')
    config_folder_name = os.path.dirname(CONFIG_FILE_NAME)
    config_filename = os.path.basename(CONFIG_FILE_NAME)

    if not os.path.exists(config_folder_name):
        os.mkdir(config_folder_name)
        print(f'Создание директории {config_folder_name}')

    with open(CONFIG_FILE_NAME, 'w') as config_file:
        config_file.write('''
[detectorInfoFile]
folderpath = config
filename = BelAES1.txt
encoding = windows-1251

[logsFile]
logfolder = logs
        ''')
        print(f'Создан файл конфигурации {CONFIG_FILE_NAME}')

    config.read(CONFIG_FILE_NAME)


def read_value(section: str, const_name: str) -> str:
    """
    Чтение значения из конфигурационного файла

    Args:
        section (str): Секция
        const_name (str): Название константы

    Returns:
        str: Значение из файла конфигурации
    """
    try:
        res = config[section][const_name]
        return res
    except KeyError:
        log.warning(f'Не найдено значение {const_name} в секции {section}')
        return None


def write_value(section: str, const_name: str, value: str):
    """
    Добавление нового (изменение имеющегося) значения
    в файл конфигурации и сохранение файла

    Args:
        section (str): Секция
        const_name (str): Название константы
        value (str): Значение константы
    """   
    config[section][const_name] = value
    with open(CONFIG_FILE_NAME, 'w') as config_file:
        config.write(config_file)
