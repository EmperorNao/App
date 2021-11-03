import pymysql.err
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore

import pandas as pd
from db.db import Database


class GUIApplication(QtWidgets.QMainWindow):

    def __init__(self, db: Database, tables=[], additional_queries={}):
        super().__init__()

        # model part
        self.db = db
        self.tables = tables
        self.additional_queries = additional_queries

        self.keys = self.tables + list(self.additional_queries.keys())
        self.current_table = None
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
        self.table.cellChanged.connect(self.changed_item)
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

    # signal
    def execute_query(self):

        button_name = self.queries.currentText()
        try:
            if button_name in self.tables:
                self.current_table = button_name

            result = self.make_request(button_name)
            self.print_result(result)
        except pymysql.err.ProgrammingError as e:
            GUIApplication.error("Error while trying to execute query", str(e), "Try select another query")

    def changed_item(self, row, col):

        if self.current_table:

            id_col_name = self.table.horizontalHeaderItem(0).text()
            id_value = self.table.item(row, 0).text()
            col_name = self.table.horizontalHeaderItem(col).text()
            new_value = self.table.item(row, col).text()
            query = f"UPDATE {self.current_table} SET {col_name} = {new_value} WHERE {id_col_name} = {id_value}"
            try:
                self.db.execute(query)
                result = self.db.select_all(self.current_table)
                self.print_result(result)

            except pymysql.err.ProgrammingError as e:
                GUIApplication.error("Error while trying to update table", str(e), "Error")

            except pymysql.err.IntegrityError as e:
                GUIApplication.error("Error while trying to update table, trouble with foreign keys", str(e), "Error")

            except:
                GUIApplication.error("Error", "Error", "Error")

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
