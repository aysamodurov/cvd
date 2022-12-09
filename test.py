from models import DetectorsInfo
import app_logger


app_logger.init_logger()
detectors_info = DetectorsInfo()
detectors_info.load_from_file()



info = detectors_info.get_info('10JKS28FG906XQ01')
print(info)
