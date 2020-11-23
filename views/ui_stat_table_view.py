'''вкладка Статистика'''
from PyQt5 import QtWidgets, QtCore

class StatisticTableWidget(QtWidgets.QWidget):

    def __init__(self, detectorController, parent = None):
        super().__init__(parent)
        self.detectorController = detectorController
        vbox = QtWidgets.QVBoxLayout()
        # таблица для отображения статистики
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(["KKS", "Среднее значение", "СКО", "Погрешность"])
        self.table.resizeColumnsToContents()

        # кнопка скопировать статистику
        self.btnCopyStat = QtWidgets.QPushButton('Скопировать')

        vbox.addWidget(self.table)
        vbox.addWidget(self.btnCopyStat)
        self.btnCopyStat.clicked.connect(self.copy_stat)
        self.setLayout(vbox)

    @QtCore.pyqtSlot()
    def copy_stat(self):
        print('Copy stats')
        res = 'KKS\tСреднее\tСКО\tПогрешность\n'
        for i in range(0, self.table.rowCount()):
            kks = self.table.model().index(i, 0).data()
            mean = self.table.model().index(i, 1).data()
            sko = self.table.model().index(i, 2).data()
            error = self.table.model().index(i, 3).data()
            res = '{}{}\t{}\t{}\t{}\n'.format(res, kks, mean, sko, error)
        print(res)
        QtWidgets.QApplication.clipboard().setText(res)


    # заполнение таблицы
    # stats - [kks, {'mean' : self.mean, 'sko' : self.sko, 'error': self.error}]
    def fill_table(self, stats):
        print('fill table')
        # заполняю построчно таблицу
        for stat in stats:
            rowPos = self.table.rowCount()
            self.table.insertRow(rowPos)
            self.table.setItem(rowPos, 0, QtWidgets.QTableWidgetItem(stat[0])) #KKS
            self.table.setItem(rowPos, 1, QtWidgets.QTableWidgetItem('{:2.5f}'.format(stat[1]['mean']))) #mean
            self.table.setItem(rowPos, 2, QtWidgets.QTableWidgetItem('{:2.5f}'.format(stat[1]['sko']))) #SKO
            self.table.setItem(rowPos, 3, QtWidgets.QTableWidgetItem('{:2.5f}'.format(stat[1]['error'])))
            self.table.resizeColumnsToContents()