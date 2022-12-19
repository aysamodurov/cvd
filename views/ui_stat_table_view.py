'''вкладка Статистика'''
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
import logging

log = logging.getLogger(__name__)


class StatisticTableWidget(QtWidgets.QWidget):

    def __init__(self, detectorController, parent=None):
        super().__init__(parent)
        self.detectorController = detectorController
        vbox = QtWidgets.QVBoxLayout()
        
        # таблица для отображения статистики
        self.column_names = detectorController.get_statistic_table_headers()
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(len(self.column_names))
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(self.column_names)
        self.table.resizeColumnsToContents()

        # кнопка скопировать статистику
        self.btnCopyStat = QtWidgets.QPushButton('Скопировать')

        vbox.addWidget(self.table)
        vbox.addWidget(self.btnCopyStat)
        self.btnCopyStat.clicked.connect(self.copy_stat)
        self.setLayout(vbox)

    @QtCore.pyqtSlot()
    def copy_stat(self):
        log.info('Копирование таблицы со статистикой в буфер обмена')
        res = '\t'.join(self.column_names) + '\n'
        
        for row in range(self.table.rowCount()):
            row_values = [self.table.item(row, column).text().strip() for column in range(self.table.columnCount())]
            res += '\t'.join(row_values) + '\n'
        QtWidgets.QApplication.clipboard().setText(res)

    # заполнение таблицы
    def fill_table(self, rows):
        log.info('Заполнение таблицы со статистикой')
        
        # столбец с выбросами 
        
        # очищаю таблицу отстарых дынных
        self.table.setRowCount(0)
        for row in rows:
            number_new_row = self.table.rowCount()
            self.table.insertRow(number_new_row)
            for number_column, value in enumerate(row):
                self.table.setItem(number_new_row, number_column, QtWidgets.QTableWidgetItem(value[0]))
                if not value[1]:
                    self.table.item(number_new_row, number_column).setBackground(QColor(255,0,0))
            self.table.resizeColumnsToContents()
        