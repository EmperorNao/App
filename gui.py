import os
import pandas as pd
import pymysql.cursors

from db import Database

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton


class GUIApplication(QtWidgets.QMainWindow):

    def __init__(self, db: Database, tables=[], additional_queries={}):

        # model part
        self.db = db
        self.tables = []
        self.additional_queries = {}

        # UI part
        self.general_layout = QGridLayout()

        self.buttons = []
        self.buttons += [QPushButton(table_name) for table_name in tables]

        self._init_left()
        self._init_right()

    def _init_left(self):

        self.button_layout = QGridLayout()
        self.general_layout.addLayout(self.buttons, 0, 0)

    def _init_right(self):
        pass

    def make_request(self, button_name):

        result = {}
        request = button_name

        if request in self.tables:
            result = self.db.select_all(request)
        elif request in self.additional_queries.keys():
            result = self.db.execute(self.additional_queries[request])

        return result

    def button_click(self):

        clicked_button = self.sender()
        button_name = clicked_button.text()
        result = self.make_request(button_name)
        self.print_result(result)

    def print_result(self, result: pd.DataFrame):
        pass

    def run(self):
        self.exec_()
