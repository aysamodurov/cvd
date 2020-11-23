'''вкладка Статистика'''
from PyQt5 import QtWidgets

class StatisticTableWidget(QtWidgets.QWidget):

    def __init__(self, detectorController, parent = None):
        super().__init__(parent)
        self.detectorController = detectorController
        vbox = QtWidgets.QVBoxLayout()
        self.buttonDelete = QtWidgets.QPushButton('Delete')
        vbox.addWidget(self.buttonDelete)
        self.setLayout(vbox)
        self.buttonDelete.clicked.connect(self.on_clicked_delete)

    def on_clicked_delete(self):
        print(self.detectorController.allDetectors)