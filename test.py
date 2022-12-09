import configparser
 

config = configparser.ConfigParser()
config.read('config/settings.ini')
FOLDER = config['detectorInfoFile']['folderpath']
FILENAME = config['detectorInfoFile']['filename']
FILEPATH = f"{FOLDER}/{FILENAME}"

try:
    a = int(input('Enter first number\n'))
    b = int(input('Enter second number\n'))
except ValueError:
    print('Введено не число!!!')


try:
    a /= b
    print(a)
except ZeroDivisionError:
    print('Деление на 0 невозможно')


print(f'{a}')