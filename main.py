# подключение папок
import os
import sys
sys.path.append(os.path.abspath('models'))
sys.path.append(os.path.abspath('views'))
from ui_main_view import MyMainWindow
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
