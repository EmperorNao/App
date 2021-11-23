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
        self.engine = create_engine(f"mysql+pymysql://{config['user']}:{config['password']}@"
                                    f"{config['host']}/{config['database']}", echo=echo, future=True)
        self.session = sessionmaker(bind=self.engine)()

        self.session.flush()

        self.tables = ["Department", "Professor", "StudyGroup", "Student",
                       "TheorySubject", "Audience", "Grade", "Class"]

        self.keys = dict()
        self.objects = []
        # UI part

        self.setWindowTitle("Электронный деканат")
        self.setMaximumSize(800, 800)

        self.general_layout = QHBoxLayout()
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.general_layout)

        self._init_left()
        self._init_right()

    def _init_left(self):

        self.max_left_width = 250
        self.layout = QVBoxLayout()

        self.entities = QComboBox()
        self.entities.setFixedWidth(self.max_left_width)

        for table in self.tables:
            self.entities.addItem(table)

        self.filters = QComboBox()
        self.filters.setFixedWidth(self.max_left_width)

        self.list = QListWidget()
        self.list.setFixedWidth(self.max_left_width)

        self.new = QPushButton("Создать пустой объект")
        self.update_btn = QPushButton("Подтвердить создание")
        self.delete = QPushButton("Удалить объект")

        self.layout.addWidget(self.entities, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.filters, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.new, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.update_btn, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.delete, QtCore.Qt.AlignTop)
        self.layout.addWidget(self.list, QtCore.Qt.AlignTop)

        # signals
        self.list.clicked.connect(self.element_clicked)
        self.entities.textActivated.connect(self.text_selected)
        self.filters.textActivated.connect(self.text_selected)
        self.new.clicked.connect(self.new_object)
        self.update_btn.clicked.connect(self.update)
        self.delete.clicked.connect(self.delete_object)

        self.general_layout.addLayout(self.layout)
        self.update_left()

    def _init_right(self):

        self.table = QTableWidget(self)  # Создаём таблицу
        self.table.cellChanged.connect(self.changed_item)

        self.general_layout.addWidget(self.table, QtCore.Qt.AlignCenter)

    def update_list(self):

        current = self.entities.currentText()
        self.list.clear()
        self.keys = dict()
        self.objects = []
        filter = self.filters.currentText()
        for index, instance in enumerate(self.session.query(OrmFactory(current))):
            self.list.addItem(str(instance.id) + ": " + str(getattr(instance, filter)))
            self.objects.append(instance)
            self.keys[instance.id] = index

    def update_left(self):

        self.filters.clear()
        current = self.get_current_table()
        attributes = class_to_columns(current)
        for a in attributes:
            self.filters.addItem(a)

        self.update_list()

    def get_current_table(self):

        return self.entities.currentText()

    def get_current_filter(self):

        return self.filters.currentText()

    def next_key(self):

        return max([el.id for el in self.objects] + [-1]) + 1

    def new_object(self):

        class Temp:
            def __init__(self, str):
                self.str = str
            def data(self):
                return self.str

        table = self.get_current_table()
        filter = self.get_current_filter()
        obj = OrmFactory(table)()
        obj.id = self.next_key()
        print(obj.id)
        self.objects.append(obj)
        self.keys[obj.id] = len(self.keys.keys())
        self.list.addItem(str(obj.id) + ": " + str(getattr(obj, filter)))
        self.list.setCurrentRow(len(self.keys) - 1)

    def update(self):

        id_value = self.table.item(0, 0).text()
        index = self.keys[int(id_value)]
        obj = self.objects[index]
        try:
            self.session.add(obj)
            self.session.commit()
        except BaseException as e:
            ORMApplication.error("Ошибка при добавлении", str(e), "Ошибка")

    def delete_object(self):

        pass

    def text_selected(self, s):

        if s in self.tables:
            self.update_left()
        else:
            self.update_list()

    def changed_item(self, row, col):

        self.table.cellChanged.disconnect(self.changed_item)

        id_value = self.table.item(0, 0).text()
        new_value = self.table.item(row, 0).text()
        index = self.keys[int(id_value)]

        col_name = self.table.verticalHeaderItem(row).text()
        self.table.horizontalHeader()

        setattr(self.objects[index], col_name, new_value)

        self.table.cellChanged.connect(self.changed_item)

    def element_clicked(self, item):

        id = int(item.data().split(": ")[0])
        obj = self.objects[self.keys[id]]

        result = {}
        # disconnect from table
        #self.table.cellChanged.disconnect(self.element_clicked)

        self.table.cellChanged.disconnect(self.changed_item)
        self.table.setColumnCount(0)
        self.table.setRowCount(0)

        #columns = ["Атрибуты", "Значения"]
        attributes = ["id"] + class_to_columns(self.entities.currentText())
        self.table.setColumnCount(1)
        self.table.setRowCount(len(attributes))

        self.table.setHorizontalHeaderLabels(["Значения"])
        self.table.setVerticalHeaderLabels(attributes)
        #for i in range(0, len(columns)):
        #    self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)

        for i, row in enumerate(attributes):
            for j, col in enumerate(["Значение"]):
                self.table.setItem(i, j, QTableWidgetItem(str(getattr(obj, attributes[i]))))

        self.table.resizeColumnsToContents()
        self.table.cellChanged.connect(self.changed_item)

        # reconnect to table
        #self.table.cellChanged.connect(self.element_clicked)

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
