# -*- coding: utf-8 -*-
'''
View вкладки График
'''
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from views.ui_navigation_toolbar import NavigationToolBar
from matplotlib.figure import Figure, Axes
import matplotlib.dates as dates
import numpy as np
import logging

log = logging.getLogger(__name__)


class Canvas(FigureCanvas):
    '''
    отрисовка графиков
    '''
    axesList = list()
    same_koef = 0.2

    def __init__(self, parent=None):
        self.fig = Figure()
        self.canvas = FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

    # отрисовка графика по заданным x,y
    def plot_graph(self, detector):
        log.info('отрисовка графика по заданным x,y')
        # AXIS LABEL
        alldates = detector.get_date_list()

        # XLABEL
        xlabel = ''

        if detector.count() == 1:
            xlabel = 'Дата и время: {}'.format(alldates[0])
        else:
            if alldates[0].strftime('%d.%m.%y') == alldates[-1].strftime('%d.%m.%y'):
                xlabel = 'Дата: {}'.format(alldates[0].strftime('%d.%m.%Y'))
            else:
                xlabel = 'Дата: {} - {}'.format(alldates[0].strftime('%d.%m.%y'), alldates[-1].strftime('%d.%m.%y'))
        ax = self.get_Axes(detector.get_value_list())
        if not ax:
            return None
        ax.set_xlabel(xlabel, weight='bold', fontsize=13)

        # YLABEL
        ax.set_ylabel(detector.get_name(), weight='bold', fontsize=13)

        # LABEL
        lbl = '{} {}'.format(detector.get_kks(), detector.get_name())

        # отрисовка линии если данные состоят из нескольких точек
        # или точки если в данных только одно значение
        line = None
        if detector.count() == 1:
            line = ax.scatter(alldates, detector.get_value_list(), label=lbl)
        else:
            line, = ax.plot(alldates, detector.get_value_list(), label=lbl)
        # обновление легенды
        self.fig.legends.clear()
        self.fig.legend(loc='lower left', fontsize=10, ncol=6, mode='expand', borderaxespad=0.)
        self.draw()
        return line

    # выбор оси из существующих или создание новой по значениям
    def get_Axes(self, data) -> Axes:
        log.info('выбор оси из существующих или создание новой по значениям')
        data = np.array(data)
        data_min = data.min()
        data_max = data.max()
        ax: Axes = None
        for ax in self.axesList:
            y_min, y_max = ax.get_ylim()
            y_min = y_min * (1 - np.sign(y_min) * self.same_koef)
            y_max = y_max * (1 + np.sign(y_max) * self.same_koef)
            if data_min > y_min and data_max < y_max:
                return ax
        if len(self.axesList) >= 4:
            msb = QtWidgets.QMessageBox()
            msb.setText('Невозможно добавить более 4 осей')
            msb.exec_()
            return None
        if not self.axesList:
            ax = self.fig.add_subplot()
            ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
            ax.grid(b=True)
        else:
            ax = self.axesList[0].twinx()
            ax._get_lines.prop_cycler = self.axesList[0]._get_lines.prop_cycler
        self.axesList.append(ax)
        if len(self.axesList) > 2:
            pos = 'left'
            if len(self.axesList) % 2 == 0:
                pos = 'right'
            ax.yaxis.set_ticks_position(pos)
            ax.yaxis.set_label_position(pos)
            ax.spines[pos].set_position(('outward', 60))
        ax.set_position([0.1, 0.18, 0.8, 0.78])
        return ax

#     удаление всех графиков
    def clear_axes(self):
        log.info('удаление всех графиков')
        for ax in self.axesList:
            ax.clear()
        self.axesList.clear()
        self.draw()


class MainCanvasWidget(QtWidgets.QWidget):
    '''
        Основное окно с графиком и дополнительными элементами
    '''
    lines = {}

    def __init__(self, parent):
        super().__init__(parent)
        vbox = QtWidgets.QVBoxLayout()
        self.canvas = Canvas(self)
        self.navigation = NavigationToolBar(self.canvas, self)
        self.buttonDelete = QtWidgets.QPushButton('Delete')
        vbox.addWidget(self.canvas, 1)
        vbox.addWidget(self.navigation, 1)
        vbox.addWidget(self.buttonDelete)
        self.setLayout(vbox)
        self.buttonDelete.clicked.connect(self.on_clicked_delete)

    def on_clicked_delete(self):
        log.info('Нажатие кнопки удалить график')
        if self.lines:
            _, line = self.lines.popitem()
            line.remove()
            leg = self.canvas.fig.legends.pop()
            self.canvas.fig.legend(loc='lower left', fontsize=10, ncol=6)
            self.canvas.draw()

    # отрисовка графика
    def plot(self, detector):
        log.info(f'Отрисовка графика {detector.get_kks()}')
        kks = detector.get_kks()
        if kks not in self.lines.keys():
            line = self.canvas.plot_graph(detector)
            if line:
                self.lines[detector.get_kks()] = line

    # удаление всех графиков
    def clear(self):
        log.info('Удаление всех графиков')
        self.lines.clear()
        self.canvas.clear_axes()

#     рисование нового графика предварительно очистив оси
    def new_plot(self, detector):
        log.info('Рисование нового графика предварительно очистив оси')
        self.clear()
        self.plot(detector)
