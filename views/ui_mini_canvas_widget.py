# -*- coding: utf-8 -*-
'''
Отрисовка графика на вкладке Данные
'''
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolBar
from matplotlib.figure import Figure, Axes
import matplotlib.dates as dates


class Canvas(FigureCanvas):
    '''
    Отрисовка графика
    '''
    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax: Axes = self.fig.add_subplot()
        self.ax.set_position([0.1, 0.1, 0.89, 0.88])
        self.canvas = FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

    # отрисовка графика по заданным x,y
    def plot_graph(self, x=None, y=None, lbl=''):
        print('plot_graph')
        xlabel = ''
        if len(x) == 1:
            self.ax.scatter(x, y, label=lbl)
            xlabel = 'Дата и время: {}'.format(x[0])
        else:
            self.ax.plot(x, y, label=lbl)
            if x[0].strftime('%d.%m.%y') == x[-1].strftime('%d.%m.%y'):
                xlabel = 'Дата: {}'.format(x[0].strftime('%d.%m.%Y'))
            else:
                xlabel = 'Дата: {} - {}'.format(x[0].strftime('%d.%m.%y'), x[-1].strftime('%d.%m.%y'))

        self.ax.set_ylabel('Значение', weight='bold', fontsize=13)
        self.ax.set_xlabel(xlabel, weight='bold', fontsize=13)
        self.ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
        self.ax.grid()
        self.ax.legend(loc='lower right')
        self.draw()

    # отрисовка горизонтальной линии
    def draw_hlines(self, x, minVal=0, maxVal=0):
        print('draw h line')
        if minVal == maxVal == 0:
            minVal, maxVal = self.ax.get_ylim()
        self.ax.vlines(x, minVal, maxVal, color='red', linewidth=2)
        self.draw()

    # удаление всех графиков
    def clear_axes(self):
        self.ax.clear()
        self.draw()


class MiniCanvasWidget(QtWidgets.QWidget):
    '''
        Окно с графиком и дополнительными элементами
    '''

    def __init__(self, parent):
        super().__init__(parent)

        vbox = QtWidgets.QVBoxLayout()
        self.canvas = Canvas(self)
        self.navigation = NavigationToolBar(self.canvas, self)
        vbox.addWidget(self.canvas, 1)
        vbox.addWidget(self.navigation, 1)
        self.setLayout(vbox)

    # отрисовка графика
    def plot(self, detector, minOptimalTime=None, maxOptimalTime=None):
        print('plot')
        # расчет статистики для датчика
        stat = detector.get_statistic()
        lbl = ''
        prec = 4-len(str(int(stat['mean'])))
        if prec < 0:
            prec = 0
        for name, val in stat.items():
            lbl += '{} : {:{width}.{pr}f}\n'.format(name, val,  width=3, pr=prec)
        self.canvas.plot_graph(detector.get_date_list(), detector.get_value_list(), lbl)
        # отрисовка вертикальных линий,
        # которые выделяют рекомедуемое для расчета время
        if minOptimalTime and maxOptimalTime:
            minVal = min(detector.get_value_list())
            maxVal = max(detector.get_value_list())
            self.canvas.draw_hlines(minOptimalTime, minVal, maxVal)
            self.canvas.draw_hlines(maxOptimalTime, minVal, maxVal)

    # удаление всех графиков
    def clear(self):
        self.canvas.clear_axes()

    # рисование нового графика предварительно очистив оси
    def new_plot(self, detector):
        self.clear()
        self.plot(detector)
