# -*- coding: utf-8 -*-
'''
View вкладки Данные
'''
from PyQt5 import QtWidgets, QtCore, QtGui
import re
from ui_mini_canvas_widget import MiniCanvasWidget
from ma_detector import MaDetector
from smooth_detector import SmoothDetector

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
        
        dateBox = QtWidgets.QHBoxLayout()
        dateBox.addWidget(QtWidgets.QLabel('Начало:'))
        dateBox.addWidget(self.startTimeEdit, QtCore.Qt.AlignLeft)
        dateBox.addWidget(QtWidgets.QLabel('Окончание:'))
        dateBox.addWidget(self.finishTimeEdit, QtCore.Qt.AlignLeft)
                
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
        
        self.kksView.installEventFilter(self)
        self.canvasWidget.customContextMenuRequested.connect(self.canvas_context_menu)
    
   
    @QtCore.pyqtSlot()
    def on_clicked_open_file(self):
        '''Открыть файлы с данными, удалить старые данные'''
        print('on_clicked_open_file')
        filesNames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open files')[0]
        if filesNames:
            self.open_files(filesNames, isNewList=True)

    @QtCore.pyqtSlot()
    def on_clicked_add_file(self):
        '''Добавить файлы с данными в имеющийя список'''
        print('on_clicked_add_file')
        filesNames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open files')[0]
        if filesNames:
            self.open_files(filesNames, isNewList=False)
    
    @QtCore.pyqtSlot()        
    def on_changed_item(self):
        '''Выбор другого датчика из списка'''
        print('on_changed_item')
        # получаю kks
        if self.kksView.currentRow() != -1:
            current_kks = self.kksView.model().data(self.kksView.currentIndex())
            self.detectorController.update_current_detector(current_kks)
            self.canvasWidget.new_plot(self.detectorController.currentDetector)
            self.update_date_time()
    
    @QtCore.pyqtSlot()    
    def on_change_datetime(self):
        '''перерисовка при изменении времени'''
        print('on_change_datetime')
        if self.changeDateTime:
            self.detectorController.update_date(self.startTimeEdit.dateTime().toPyDateTime(),
                                                self.finishTimeEdit.dateTime().toPyDateTime())
            self.detectorController.update_current_detector()
            self.update_date_time()
            self.canvasWidget.new_plot(self.detectorController.currentDetector)

    @QtCore.pyqtSlot()
    def changed_kks_mask(self):
        ''' Ввод данных в поле маска '''
        print('changed_kks_mask')
        reg = self.kksFilterEdit.text().strip()
        if reg== '':
            reg+='*'
        reg = (reg.replace('*','.*')+'$').upper()
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
        print('on_reset_time')
        self.detectorController.reset_start_finish_date()
        self.detectorController.update_current_detector()
        self.update_date_time()
        self.canvasWidget.new_plot(self.detectorController.currentDetector)

    @QtCore.pyqtSlot()
    def on_choose_optimal_time(self):
        print('Выбор оптимального времени')
        #отображение анимации
        splashCalc = QtWidgets.QSplashScreen(QtGui.QPixmap(r"pic/loading.gif"))
        splashCalc.resize(200, 200)
        splashCalc.show()
        QtWidgets.qApp.processEvents()
        splashCalc.showMessage("Выбор времени для рсчета",
                                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
        #выбор оптимального времени для расчета
        ts, tf =self.detectorController.get_optimal_time()
        print('111', ts,tf)
        #перирисовка графика с полученным временем
        if ts:
            self.startTimeEdit.setDateTime(ts)
            self.finishTimeEdit.setDateTime(tf)
        splashCalc.close()

            
    # DRAG AND DROP
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()
             
    def dropEvent(self,e):
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
            menu.addAction('Скользящее среднее', self.on_mooving_avarage)
            if menu.exec_(event.globalPos()):
                item:QtWidgets.QListWidgetItem = source.itemAt(event.pos())
        return super(DataWidget,self).eventFilter(source,event)
    
    # МЕНЮ ПРИ НАЖАТИИ НА ГРАФИК
    def canvas_context_menu(self,point):
        menu = QtWidgets.QMenu()
        menu.addAction('Сбросить время', self.on_reset_time)
        menu.addAction('Выбор стабильного состояния', self.on_choose_optimal_time)
        menu.exec_(self.canvasWidget.mapToGlobal(point))     
    
#     ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    def open_files(self, filesNames, isNewList = False):
        '''загрузка файлов
        при загрузке отображается картинка Loading'''
        print('open_files')
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
        print('finish_open')

    def update_kks_view(self):
        ''' Обновление kksList
        удаляет старый и создает новый ListView'''
        print('update_kks_view')
        self.kksView.clear()
        self.kksView.addItems(self.detectorController.allDetectors.get_all_kks())
        self.kksView.setCurrentRow(0)
        self.changed_kks_mask()
    
    def update_date_time(self):
        '''обновить дату и время начала и окнчания данных'''
        print('update_date_time')
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
        print('on_smoothing')
        koef, ok = QtWidgets.QInputDialog.getDouble(self,'Сглаживание данных', 'Введите коэффициент сглаживания',
                                                 value = 0.8, min = 0.0, max = 1.0, decimals = 2)
        if ok:
            smDetector = SmoothDetector(self.detectorController.currentDetector,koef)
            isNew = self.detectorController.allDetectors.insert(smDetector)
            if isNew:
                self.kksView.addItem(smDetector.kks)
                self.kksView.setCurrentRow(self.kksView.count()-1)
        
            
    def on_mooving_avarage(self):
        '''расчет с применением коскользящего среднего'''
        print('on_mooving_avarage')
        koef, ok = QtWidgets.QInputDialog.getInt(self,'Скользящее среднее', 'Период скользящей средней',
                                                 value=10, min=2, max=100, step=1)
        if ok:
            maDetector = MaDetector(self.detectorController.currentDetector,koef)
            isNew = self.detectorController.allDetectors.insert(maDetector)
            if isNew:
                self.kksView.addItem(maDetector.kks)
                self.kksView.setCurrentRow(self.kksView.count()-1)
                   
    def on_new_main_plotting(self):
        '''построение новых графиков в новом окне на вкладке график'''
        print('on_new_main_plotting')
        self.parent.mainCanvas.clear()

        for ind in self.kksView.selectedIndexes():
            kks = self.kksView.model().data(ind)
            detector = self.detectorController.allDetectors.get_detector_by_kks(kks)
            self.parent.mainCanvas.plot(detector)
        self.parent.tabWidget.setCurrentIndex(1)
    
    def on_add_main_plotting(self):
        '''добавление графика к существующим на вкладке график'''
        print('on_add_main_plotting')
        for ind in self.kksView.selectedIndexes():
            kks = self.kksView.model().data(ind)
            detector = self.detectorController.allDetectors.get_detector_by_kks(kks)
            self.parent.mainCanvas.plot(detector)
        self.parent.tabWidget.setCurrentIndex(1)
