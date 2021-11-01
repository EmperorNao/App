from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore

import pandas as pd
from db import Database


class GUIApplication(QtWidgets.QMainWindow):

    def __init__(self, db: Database, tables=[], additional_queries={}):
        super().__init__()

        # model part
        self.db = db
        self.tables = tables
        self.additional_queries = additional_queries

        self.keys = self.tables + list(self.additional_queries.keys())
        # UI part

        self.setWindowTitle("University GUI")
        self.setBaseSize(500, 500)

        self.general_layout = QVBoxLayout()
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.general_layout)

        self._init_top()
        self._init_bottom()

    def _init_top(self):

        self.button_layout = QGridLayout()

        self.queries = QComboBox()
        self.queries.setMaximumWidth(10 * max([len(s) for s in self.keys]))
        for table_name in self.tables:
            self.queries.addItem(table_name)

        for query_name in self.additional_queries.keys():
            self.queries.addItem(query_name)

        self.execute = QPushButton("Execute")
        self.execute.setFixedWidth(100)
        self.execute.clicked.connect(self.execute_query)

        self.button_layout.addWidget(self.queries, 0, 0, QtCore.Qt.AlignLeft)
        self.button_layout.addWidget(self.execute, 0, 1, QtCore.Qt.AlignRight)
        self.general_layout.addLayout(self.button_layout)

    def _init_bottom(self):

        self.table = QTableWidget(self)  # Создаём таблицу
        self.general_layout.addWidget(self.table)

    def make_request(self, button_name):

        result = {}
        request = button_name

        if request in self.tables:
            result = self.db.select_all(request)
        elif request in self.additional_queries.keys():
            result = self.db.execute(self.additional_queries[request])

        return result

    def print_result(self, result: pd.DataFrame):

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

    # signal
    def execute_query(self):

        button_name = self.queries.currentText()
        result = self.make_request(button_name)
        self.print_result(result)
