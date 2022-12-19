# -*- coding: utf-8 -*-
'''
View вкладки Данные
'''
from PyQt5 import QtWidgets, QtCore, QtGui
import re
from views.ui_mini_canvas_widget import MiniCanvasWidget
from models import MaDetector
from models import SmoothDetector
import config
import os
import logging

log = logging.getLogger(__name__)


class DataWidget(QtWidgets.QWidget):
    '''
        Виджет для отображения в первой вкладке приложения
        на нем расположен список с kks, фильтр, и график
        '''

    def __init__(self, detectorController, parent=None):
        super().__init__(parent)
        changeDateTime = True
        self.parent = parent
        self.detectorController = detectorController

        # картинка при загрузке файла
        self.splash = QtWidgets.QSplashScreen(QtGui.QPixmap(r"pic/loading.jpg"))
        self.splash.resize(120, 140)

        #         ЛЕВАЯ ЧАСТЬ ЭКРАНА

        # кнопка открыть файл
        self.btnOpenFile = QtWidgets.QPushButton('Открыть новый файл')
        # фильтр для kks
        kksFilterBox = QtWidgets.QHBoxLayout()
        kksFilterBox.addWidget(QtWidgets.QLabel('Маска:'))
        self.kksFilterEdit = QtWidgets.QLineEdit()
        kksFilterBox.addWidget(self.kksFilterEdit)
        # listView для списка kks
        self.kksView = QtWidgets.QListWidget()
        self.kksView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        leftBox = QtWidgets.QVBoxLayout()
        leftBox.addWidget(self.btnOpenFile)
        leftBox.addLayout(kksFilterBox)
        leftBox.addWidget(self.kksView)

        #         ПРАВАЯ ЧАСТЬ ЭКРАНА
        # MPL для рисования графика
        self.canvasWidget = MiniCanvasWidget(self)
        self.canvasWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # Дата и время для начала и окончания построения графика
        self.startTimeEdit = QtWidgets.QDateTimeEdit()
        self.startTimeEdit.setDisplayFormat('dd.MM.yyyy HH:mm:ss')
        self.finishTimeEdit = QtWidgets.QDateTimeEdit()
        self.finishTimeEdit.setDisplayFormat('dd.MM.yyyy HH:mm:ss')
        self.btnCalcStat = QtWidgets.QPushButton('Расчитать статистику')

        dateBox = QtWidgets.QHBoxLayout()
        dateBox.addWidget(QtWidgets.QLabel('Начало:'))
        dateBox.addWidget(self.startTimeEdit, QtCore.Qt.AlignLeft)
        dateBox.addWidget(QtWidgets.QLabel('Окончание:'))
        dateBox.addWidget(self.finishTimeEdit, QtCore.Qt.AlignLeft)
        dateBox.addWidget(self.btnCalcStat)

        #         ГЛАВНЫЙ ЭКРАН
        mainBox = QtWidgets.QGridLayout()
        mainBox.addLayout(leftBox, 0, 0, 2, 1)
        mainBox.setColumnStretch(0, 0)
        mainBox.addWidget(self.canvasWidget, 0, 1, 1, 1)
        mainBox.addLayout(dateBox, 1, 1, 1, 1)
        mainBox.setColumnStretch(1, 1)
        self.setLayout(mainBox)
        self.setAcceptDrops(True)

        #         ОБРАБОТЧИКИ СОБЫТИЙ
        self.btnOpenFile.clicked.connect(self.on_clicked_open_file)
        self.kksFilterEdit.textChanged.connect(self.changed_kks_mask)
        self.kksView.currentItemChanged.connect(self.on_changed_item)
        self.startTimeEdit.dateTimeChanged.connect(self.on_change_datetime)
        self.finishTimeEdit.dateTimeChanged.connect(self.on_change_datetime)
        self.btnCalcStat.clicked.connect(self.on_calc_stats)

        self.kksView.installEventFilter(self)
        self.canvasWidget.customContextMenuRequested.connect(self.canvas_context_menu)

    @QtCore.pyqtSlot()
    def on_clicked_open_file(self):
        '''Открыть файлы с данными, удалить старые данные'''
        log.info('Нажатие кнопки открыть файлы с данными')
        filesNames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open files')[0]
        if filesNames:
            self.open_files(filesNames, isNewList=True)

    @QtCore.pyqtSlot()
    def on_clicked_add_file(self):
        '''Добавить файлы с данными в имеющийя список'''
        log.info('Нажатие кнопки добавить файлы с данными')
        filesNames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open files')[0]
        if filesNames:
            self.open_files(filesNames, isNewList=False)

    @QtCore.pyqtSlot()
    def on_clicked_change_info_file(self):
        """
        Изменить файл с информацией о датчиках
        """
        log.info('Изменение файла с информацией о датчиках')
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Выбрать файл с информацией о датчиках')[0]
        if file_path:
            config_folder_name = os.path.dirname(file_path)
            config_filename = os.path.basename(file_path)
            config.write_value('detectorInfoFile', 'folderpath', config_folder_name)
            config.write_value('detectorInfoFile', 'filename', config_filename)
            log.info(f'Изменен файл с настроечной информацией о датчиках {file_path}')
            self.detectorController.update_all_description()

    @QtCore.pyqtSlot()
    def on_changed_item(self):
        '''Выбор другого датчика из списка'''
        log.info('Изменение текущего датчика')
        # получаю kks
        if self.kksView.currentRow() != -1:
            current_kks = self.kksView.model().data(self.kksView.currentIndex())
            self.detectorController.update_current_detector(current_kks)
            self.canvasWidget.new_plot(self.detectorController.currentDetector)
            self.update_date_time()

    @QtCore.pyqtSlot()
    def on_change_datetime(self):
        '''перерисовка при изменении времени'''
        log.info('Изменение времени выборки')
        if self.changeDateTime:
            self.detectorController.update_date(self.startTimeEdit.dateTime().toPyDateTime(),
                                                self.finishTimeEdit.dateTime().toPyDateTime())
            self.detectorController.update_current_detector()
            self.update_date_time()
            self.canvasWidget.new_plot(self.detectorController.currentDetector)

    @QtCore.pyqtSlot()
    def changed_kks_mask(self):
        ''' Ввод данных в поле маска '''
        reg = self.kksFilterEdit.text().strip()
        log.info(f'Ввод данных в поле маска {reg}')
        if reg == '':
            reg += '*'
        reg = (reg.replace('*', '.*') + '$').upper()
        changeKksList = list()
        for detect in self.detectorController.allDetectors:
            kks = detect.get_kks()
            res = re.match(reg, kks)
            if res:
                changeKksList.append(kks)
        self.kksView.clear()
        self.kksView.addItems(changeKksList)

    @QtCore.pyqtSlot()
    def on_reset_time(self):
        '''сброс времени(отрисовка всех данных по датчику)'''
        log.info('Сброс времени выборки')
        self.detectorController.reset_start_finish_date()
        self.detectorController.update_current_detector()
        self.update_date_time()
        self.canvasWidget.new_plot(self.detectorController.currentDetector)

    @QtCore.pyqtSlot()
    def on_choose_optimal_time(self):
        log.info('Выбор оптимального времени')
        # отображение анимации
        splashCalc = QtWidgets.QSplashScreen(QtGui.QPixmap(r"pic/loading.gif"))
        splashCalc.resize(200, 200)
        splashCalc.show()
        QtWidgets.qApp.processEvents()
        splashCalc.showMessage("Выбор времени для рсчета",
                               QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
        # выбор оптимального времени для расчета
        ts, tf = self.detectorController.get_optimal_time()
        # перирисовка графика с полученным временем
        if ts:
            self.startTimeEdit.setDateTime(ts)
            self.finishTimeEdit.setDateTime(tf)
        splashCalc.close()

    @QtCore.pyqtSlot()
    def on_calc_stats(self):
        if not self.detectorController.currentDetector:
            log.warning(f'Не задан текущий датчик')
            return
        log.info('Вычисление статистических показателей')
        rows = self.detectorController.get_statisctic_table_rows()
        self.parent.statTable.fill_table(rows)
        self.parent.tabWidget.setCurrentIndex(2)

    # DRAG AND DROP
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        urls = e.mimeData().urls()
        filesNames = [url.path()[1:] for url in urls]
        self.open_files(filesNames, isNewList=False)

    # МЕНЮ ПРИ НАЖАТИИ НА СПИСОК
    def eventFilter(self, source, event):
        '''обработка событий при клике на listview'''
        if (event.type() == QtCore.QEvent.ContextMenu and source is self.kksView):
            menu = QtWidgets.QMenu()
            menu.addAction('Построить новый график', self.on_new_main_plotting)
            menu.addAction('Добавить график', self.on_add_main_plotting)
            menu.addAction('Произвести сглаживание', self.on_smoothing)
            menu.addAction('Подбор коэффициента сглаживания', self.on_calc_smooth)
            menu.addAction('Скользящее среднее', self.on_mooving_avarage)
            if menu.exec_(event.globalPos()):
                item: QtWidgets.QListWidgetItem = source.itemAt(event.pos())
        return super(DataWidget, self).eventFilter(source, event)

    # МЕНЮ ПРИ НАЖАТИИ НА ГРАФИК
    def canvas_context_menu(self, point):
        menu = QtWidgets.QMenu()
        menu.addAction('Сбросить время', self.on_reset_time)
        menu.addAction('Выбор стабильного состояния', self.on_choose_optimal_time)
        menu.exec_(self.canvasWidget.mapToGlobal(point))

    #     ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    def open_files(self, filesNames, isNewList=False):
        '''загрузка файлов
        при загрузке отображается картинка Loading'''
        log.info(f'Обработка файлов {filesNames}')
        self.canvasWidget.clear()
        self.splash.show()
        QtWidgets.qApp.processEvents()
        self.splash.showMessage("Загрузка {} файлов ".format(len(filesNames)),
                                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
        self.detectorController.loading_data(filesNames, isNewList)
        self.splash.close()
        self.update_kks_view()
        self.on_changed_item()
        self.parent.tabWidget.setCurrentIndex(0)
        log.info(f'Файлы {filesNames} обработаны')

    def update_kks_view(self):
        ''' Обновление kksList
        удаляет старый и создает новый ListView'''
        self.kksView.clear()
        self.kksView.addItems(self.detectorController.allDetectors.get_all_kks())
        self.kksView.setCurrentRow(0)
        self.changed_kks_mask()

    def update_date_time(self):
        '''обновить дату и время начала и окнчания данных'''
        self.changeDateTime = False
        #         обновляем дату и время, за которые есть данные
        self.startTimeEdit.setMinimumDateTime(self.detectorController.minDate)
        self.startTimeEdit.setMaximumDateTime(self.detectorController.maxDate)
        self.startTimeEdit.setDateTime(self.detectorController.startDate)
        self.finishTimeEdit.setMinimumDateTime(self.detectorController.minDate)
        self.finishTimeEdit.setMaximumDateTime(self.detectorController.maxDate)
        self.finishTimeEdit.setDateTime(self.detectorController.finishDate)
        self.changeDateTime = True

    #     сглаживание данных
    def on_smoothing(self):
        '''расчет с применением коэффициента сглаживания'''
        log.info('Расчет с применением коэффициента сглаживания')
        koef, ok = QtWidgets.QInputDialog.getDouble(self, 'Сглаживание данных', 'Введите коэффициент сглаживания',
                                                    value=0.8, min=0.0, max=1.0, decimals=2)
        if ok:
            smDetector = SmoothDetector(self.detectorController.currentDetector, koef)
            isNew = self.detectorController.allDetectors.insert(smDetector)
            if isNew:
                self.kksView.addItem(smDetector.kks)
                self.kksView.setCurrentRow(self.kksView.count() - 1)

    # подобрать коэффициент сглаживания по заданной допустимой погрешности
    def on_calc_smooth(self):
        log.info('Подбор коэффициента сглаживания')
        awailableError, ok = QtWidgets.QInputDialog.getDouble(self, 'Подбор коэффициента сглаживания',
                                                              'Введите допустимую погрешность', value=0, decimals=3)
        if ok:
            # подбор коэффициента при котором погрешность будет меньше допустимой
            # побор производится с шагом 0,05
            # перешел к 100, вместо еденицы, так как 0,9-0,05 = 0,84999
            kSmooth = 1
            while kSmooth > 0:
                kSmooth = round(kSmooth, 2)
                smDetector = SmoothDetector(self.detectorController.currentDetector, kSmooth)
                if smDetector.calculate_statistic()['error'] < awailableError:
                    break
                kSmooth -= 0.05
            # вывод результатов
            if kSmooth == 1:
                QtWidgets.QMessageBox.information(self, 'Сглаживание не требуется', 'Коэффициент сглаживания равен 1')
            elif kSmooth > 0:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText('Коэффициент сглаживания равен {}'.format(kSmooth))
                msgBox.setInformativeText('Добавить в список датчик с коэффициентом сглаживания {}?'.format(kSmooth))
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
                ret = msgBox.exec_()
                if ret == QtWidgets.QMessageBox.Ok:
                    isNew = self.detectorController.allDetectors.insert(smDetector)
                    if isNew:
                        self.kksView.addItem(smDetector.kks)
                        self.kksView.setCurrentRow(self.kksView.count() - 1)
            else:
                QtWidgets.QMessageBox.information(self, 'Внимание', 'Невозможно подобрать коэффициент сглаживания')

    def on_mooving_avarage(self):
        '''расчет с применением коскользящего среднего'''
        log.info('Расчет скользящего среднего')
        koef, ok = QtWidgets.QInputDialog.getInt(self, 'Скользящее среднее', 'Период скользящей средней',
                                                 value=10, min=2, max=100, step=1)
        if ok:
            maDetector = MaDetector(self.detectorController.currentDetector, koef)
            isNew = self.detectorController.allDetectors.insert(maDetector)
            if isNew:
                self.kksView.addItem(maDetector.kks)
                self.kksView.setCurrentRow(self.kksView.count() - 1)

    def on_new_main_plotting(self):
        '''построение новых графиков в новом окне на вкладке график'''
        log.info('построение новых графиков в новом окне на вкладке график')
        self.parent.mainCanvas.clear()

        for ind in self.kksView.selectedIndexes():
            kks = self.kksView.model().data(ind)
            detector = self.detectorController.allDetectors.get_detector_by_kks(kks)
            self.parent.mainCanvas.plot(detector)
        self.parent.tabWidget.setCurrentIndex(1)

    def on_add_main_plotting(self):
        '''добавление графика к существующим на вкладке график'''
        log.info('добавление графика к существующим на вкладке график')
        for ind in self.kksView.selectedIndexes():
            kks = self.kksView.model().data(ind)
            detector = self.detectorController.allDetectors.get_detector_by_kks(kks)
            self.parent.mainCanvas.plot(detector)
        self.parent.tabWidget.setCurrentIndex(1)
