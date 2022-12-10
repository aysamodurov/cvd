from models import DetectorsInfo
import app_logger


app_logger.init_logger()
detectors_info = DetectorsInfo()
detectors_info.load_from_file()


import config
folder_name = config.read_value('detectorInfofsdFile', 'folderpath')
print(folder_name)
config.write_value('detectorInfoFile', 'folderpath', 'config1')
# folder_name = config.read_value('detectorInfoFile', 'folderpath')
# print(folder_name)