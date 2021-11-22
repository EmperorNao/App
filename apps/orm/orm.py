from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from db.db import Database
from sqlalchemy import create_engine



class ORMApplication(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # model part
        self.engine = create_engine("mysql+pymysql://root:password@localhost:3306/university", echo=True, future=True)

        # UI part

        self.setWindowTitle("University GUI")
        self.setMaximumSize(800, 800)

        self.general_layout = QHBoxLayout()
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.general_layout)

        self._init_left()
        self._init_right()

    def _init_left(self):

        self.layout = QVBoxLayout()

        self.entities = QComboBox()
        self.entities.setFixedWidth(150)
        self.filter = QComboBox()
        self.filter.setFixedWidth(150)
        self.objects = QListWidget()
        self.objects.setFixedWidth(150)

        self.layout.addWidget(self.entities, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.filter, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.objects, QtCore.Qt.AlignTop)

        # signals
        #self.objects.clicked.connect(self.element_clicked)

        self.general_layout.addLayout(self.layout)

    def _init_right(self):

        self.table = QTableWidget(self)  # Создаём таблицу

        # signals
        # self.table.cellChanged.connect(self.changed_item)

        self.general_layout.addWidget(self.table)

    def make_request(self, button_name):

        result = {}
        request = button_name
        if request in self.tables:
            result = self.db.select_all(request)
        elif request in self.additional_queries.keys():
            result = self.db.execute(self.additional_queries[request])

        return result

    def print_result(self):

        result = {}
        # disconnect from table
        self.table.cellChanged.disconnect(self.changed_item)

        self.table.setColumnCount(0)
        self.table.setRowCount(0)

        columns = result.columns
        self.table.setColumnCount(len(columns))
        self.table.setRowCount(result.shape[0])

        self.table.setHorizontalHeaderLabels(columns)
        for i in range(0, len(columns)):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)

        for i, row in result.iterrows():
            for j, col in enumerate(columns):
                self.table.setItem(i, j, QTableWidgetItem(str(row[col])))

        self.table.resizeColumnsToContents()

        # reconnect to table
        self.table.cellChanged.connect(self.changed_item)

    # # signal
    # def execute_query(self):
    #
    #     button_name = self.queries.currentText()
    #     try:
    #         if button_name in self.tables:
    #             self.current_table = button_name
    #
    #         result = self.make_request(button_name)
    #         self.print_result(result)
    #     except ...:
    #         ORMApplication.error("Error while trying to execute query", "fuck", "Try select another query")

    # def changed_item(self, row, col):
    #
    #     if self.current_table:
    #
    #         id_col_name = self.table.horizontalHeaderItem(0).text()
    #         id_value = self.table.item(row, 0).text()
    #         col_name = self.table.horizontalHeaderItem(col).text()
    #         new_value = self.table.item(row, col).text()
    #         query = f"UPDATE {self.current_table} SET {col_name} = {new_value} WHERE {id_col_name} = {id_value}"
    #         try:
    #             self.db.execute(query)
    #             result = self.db.select_all(self.current_table)
    #             self.print_result(result)
    #         except ...:
    #             ORMApplication.error("Error", "Error", "Error")

    def element_clicked(self, item):
        self.table.setColumnCount(1)
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem(str(25)))
        print('click -> {}'.format(item.data()))

    @staticmethod
    def error(text: str = "", info_text: str = "", title: str = ""):
        """
        method to call, when error has happened
        :param text: short description of error
        :param info_text: extended error description
        :param title: window title
        :return:
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setInformativeText(info_text)
        msg.setWindowTitle(title)
        msg.exec()
