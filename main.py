# подключение папок
import os, sys
sys.path.append(os.path.abspath('models'))
sys.path.append(os.path.abspath('views'))
from ui_main_view import MyMainWindow
from PyQt5 import QtWidgets
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()