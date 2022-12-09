from views import MyMainWindow
from PyQt5 import QtWidgets
import sys
import app_logger
import logging


def main():
    app_logger.init_logger()
    logger = logging.getLogger(__name__)
    logger.info('Запуск CVD')

    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
