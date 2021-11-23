from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QPushButton
from sqlalchemy import create_engine


from apps.orm.university_objects import *
import inspect


class ORMApplication(QtWidgets.QMainWindow):

    def __init__(self, config, echo=True):
        super().__init__()

        # model part
        self.student_id = dict()
        # dict of dicts: student.id -> subject.id -> grade

        # database part part
        self.engine = create_engine(f"mysql+pymysql://{config['user']}:{config['password']}@"
                                    f"{config['host']}/{config['database']}", echo=echo, future=True)
        self.session = sessionmaker(bind=self.engine)()

        # UI part
        self.setWindowTitle("Электронный деканат")
        self.setMaximumSize(600, 600)

        self.general_layout = QVBoxLayout()
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.general_layout)

        self._init_bottom()
        self._init_top()

    def _init_top(self):

        self.top_layout = QHBoxLayout()

        self.department_box = QComboBox()
        self._init_department()
        self.group_box = QComboBox()
        self._init_group()

        self.plot_grades()

        self.update_btn = QPushButton("Подтвердить изменения")

        self.top_layout.addWidget(self.department_box, QtCore.Qt.AlignLeft)
        self.top_layout.addWidget(self.group_box, QtCore.Qt.AlignLeft)
        self.top_layout.addWidget(self.update_btn, QtCore.Qt.AlignLeft)

        # signals
        self.department_box.currentTextChanged.connect(self.update_department)
        self.group_box.currentTextChanged.connect(self.update_group)
        self.update_btn.clicked.connect(self.update)

        self.general_layout.addLayout(self.top_layout)

    def _init_bottom(self):

        self.table = QTableWidget(self)
        self.table.cellChanged.connect(self.change_grade)
        self.general_layout.addWidget(self.table, QtCore.Qt.AlignCenter)

    def _init_department(self):

        self.department_box.clear()
        departments = self.session.query(Department.id, Department.title).all()
        for id, dep in departments:
            self.department_box.addItem(str(id) + ": " + dep)

    def _init_group(self):

        self.group_box.clear()
        department_id = self.get_current_department().split(": ")[0]
        groups = self.session.query(StudyGroup.id, StudyGroup.title).filter_by(department_id=department_id).all()
        for id, group in groups:
            self.group_box.addItem(str(id) + ": " + group)

    def get_current_group(self):

        return self.group_box.currentText()

    def get_current_department(self):

        return self.department_box.currentText()

    def next_key(self):

        return max([el.id for el in self.objects] + [-1]) + 1

    def plot_grades(self):

        # clear grades
        pass

    def update_department(self, s):

        self._init_group()

    def update_group(self, s):

        self.plot_grades()

    def update(self):

        try:
            self.session.commit()
        except BaseException as e:
            ORMApplication.error("Ошибка во время попытки произвести обновление", str(e), "Ошибка")

    def change_grade(self, row, col):

        pass
        # self.table.cellChanged.disconnect(self.changed_item)
        #
        # id_value = self.table.item(0, 0).text()
        # new_value = self.table.item(row, 0).text()
        # index = self.keys[int(id_value)]
        #
        # col_name = self.table.verticalHeaderItem(row).text()
        # self.table.horizontalHeader()
        #
        # setattr(self.objects[index], col_name, new_value)
        #
        # self.table.cellChanged.connect(self.changed_item)


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
