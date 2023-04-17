# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from detector_controller import DetectorController
from views.ui_data_widget_with_description import DataWidgetWithDescription
from views import MainCanvasWidget
from views.ui_stat_table_view import StatisticTableWidget


class MyMainWindow(QtWidgets.QMainWindow):
    '''главное окно приложения
    создание окна с вкладками и основного меню
    '''
    detectorController = DetectorController()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1400, 700)
        self.setWindowTitle('CVD 0.1')

        # создание окна с вкладками
        self.tabWidget = QtWidgets.QTabWidget()

        self.dataWidget = DataWidgetWithDescription(self.detectorController, self)
        self.tabWidget.addTab(self.dataWidget, 'Данные')

        self.mainCanvas = MainCanvasWidget(self)
        self.tabWidget.addTab(self.mainCanvas, 'График')

        self.statTable = StatisticTableWidget(self.detectorController)
        self.tabWidget.addTab(self.statTable, 'Статистика')

        self.setCentralWidget(self.tabWidget)

#         ОСНОВНОЕ МЕНЮ
        bar: QtWidgets.QMenuBar = self.menuBar()
        fileMenu: QtWidgets.QMenu = bar.addMenu('Файл')
        openAction = QtWidgets.QAction('Открыть новый файл', self)
        openAction.triggered.connect(self.dataWidget.on_clicked_open_file)
        addAction = QtWidgets.QAction('Добавить файл', self)
        addAction.triggered.connect(self.dataWidget.on_clicked_add_file)
        changeInfoFileAction = QtWidgets.QAction('Выбрать файл с информацией о датчиках', self)
        changeInfoFileAction.triggered.connect(self.dataWidget.on_clicked_change_info_file)
        closeAction = QtWidgets.QAction('Закрыть', self)
        closeAction.triggered.connect(QtWidgets.qApp.quit)

        fileMenu.addAction(openAction)
        fileMenu.addAction(addAction)
        fileMenu.addAction(changeInfoFileAction)
        fileMenu.addAction(closeAction)
