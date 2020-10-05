# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets,QtCore
from detector_controller import DetectorController
from ui_data_widget import DataWidget
from ui_main_canvas import MainCanvasWidget

#     настройки для работы QT
paths = QtCore.QCoreApplication.libraryPaths()
paths.append(r"D:\рабочая\DISTR\Python\Thonny\Lib\site-packages\PyQt5\Qt\plugins")
QtCore.QCoreApplication.setLibraryPaths(paths)       

class MyMainWindow(QtWidgets.QMainWindow):
    '''главное окно приложения'''
    detectorController = DetectorController()
    
    def __init__(self,parent = None):
        super().__init__(parent)
        self.resize(1200,700)
        
        self.tabWidget = QtWidgets.QTabWidget()
        
        self.dataWidget = DataWidget(self.detectorController,self)
        self.tabWidget.addTab(self.dataWidget,'Данные')
        
        self.mainCanvas = MainCanvasWidget(self)
        self.tabWidget.addTab(self.mainCanvas,'График')
    
        self.setCentralWidget(self.tabWidget)
        
#         ОСНОВНОЕ МЕНЮ
        bar:QtWidgets.QMenuBar = self.menuBar()
        fileMenu:QtWidgets.QMenu = bar.addMenu('Файл')
        openAction = QtWidgets.QAction('Открыть новый файл',self)
        openAction.triggered.connect(self.dataWidget.on_clicked_open_file)
        addAction = QtWidgets.QAction('Добавить файл',self)
        addAction.triggered.connect(self.dataWidget.on_clicked_add_file)
        closeAction = QtWidgets.QAction('Закрыть',self)
        closeAction.triggered.connect(QtWidgets.qApp.quit)        
                
        fileMenu.addAction(openAction)
        fileMenu.addAction(addAction)
        fileMenu.addAction(closeAction)