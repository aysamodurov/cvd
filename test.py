import app_logger
import logging
from models import reader


svb_filename = 'data/20KBA10CF001_XQ01.txt'
rsa_filename = 'data/PTK-Z.rsa'


def main():
    app_logger.init_logger()
    logger = logging.getLogger(__name__)
    file_reader = reader.create_reader(svb_filename)
    detectors = file_reader.read_file()

    with open('res.txt', 'w') as res_file:
        print(detectors, file=res_file)
    # print(detectors)


if __name__ == '__main__':
    main()
