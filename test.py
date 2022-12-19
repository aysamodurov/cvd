import sys
import app_logger
import logging
from models import reader
import datetime


svb_filename = 'data/JEC_fix.txt'
rsa_filename = 'data/PTK-Z.rsa'

def main():
    app_logger.init_logger()
    logger = logging.getLogger(__name__)
    file_reader = reader.create_reader(rsa_filename)
    detectors = file_reader.read_file()
    
    kks = '10BBA00CE824XQ62'
    detect = detectors.get_detector_by_kks(kks)
    start_time = datetime.datetime.strptime('2020-01-30 18:20:25', '%Y-%m-%d %H:%M:%S')
    finish_time = datetime.datetime.strptime('2020-01-30 18:21:25', '%Y-%m-%d %H:%M:%S')
    
    detect.indication_list = list(filter(lambda x: x.dt>=start_time and x.dt<=finish_time, detect.get_indication_list()))
    
    detect2 = detectors.get_detector(kks, start_time, finish_time)
    # detect2.kks = 'aaa'
    # detect2.indication_list[0].value = 0
    
    with open('res.txt', 'w') as res_file:
        print(detect, file=res_file)
        print(detect2, file=res_file)

    

if __name__ == '__main__':
    main()
