import os

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from sqlalchemy import create_engine

from apps.orm.university_objects import *
from alembic.config import Config
from alembic import command

import json



class ORMApplication(QtWidgets.QMainWindow):

    def __init__(self, config, echo=True):
        super().__init__()

        # model part
        self.student_id = dict()
        self.backup_name = r".\backup\backup.json"
        # dict of dicts: student.id -> subject.id -> grade

        # database part part
        self.engine = create_engine(f"mysql+pymysql://{config['user']}:{config['password']}@"
                                    f"{config['host']}/{config['database']}", echo=echo, future=True)
        self.session = sessionmaker(bind=self.engine)()
        self.config = Config("alembic.ini")

        # UI part
        self.setWindowTitle("Электронная ведомость")
        self.setMaximumSize(1336, 600)

        self.general_layout = QVBoxLayout()
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.general_layout)

        self._init_bottom()
        self._init_top()

    # prepare or reamke qt items
    def _init_top(self):

        self.top_layout = QHBoxLayout()

        self.department_box = QComboBox()
        self._init_department()
        self.group_box = QComboBox()
        self._init_group()

        self.plot_grades()

        self.update_btn = QPushButton("Подтвердить изменения")

        self.upgrade_db_btn = QPushButton("Создать резервную копию")
        self.downgrade_db_btn = QPushButton("Загрузить резервную копию")
        self.update_call_btn = QPushButton("Обновить таблицу")

        self.top_layout.addWidget(self.department_box, QtCore.Qt.AlignLeft)
        self.top_layout.addWidget(self.group_box, QtCore.Qt.AlignLeft)
        self.top_layout.addWidget(self.update_btn, QtCore.Qt.AlignLeft)
        self.top_layout.addWidget(self.upgrade_db_btn, QtCore.Qt.AlignLeft)
        self.top_layout.addWidget(self.downgrade_db_btn, QtCore.Qt.AlignLeft)
        self.top_layout.addWidget(self.update_call_btn, QtCore.Qt.AlignLeft)

        # signals
        self.department_box.currentTextChanged.connect(self.update_department)
        self.group_box.currentTextChanged.connect(self.update_group)
        self.update_btn.clicked.connect(self.update)
        self.upgrade_db_btn.clicked.connect(self.upgrade_db)
        self.downgrade_db_btn.clicked.connect(self.downgrade_db)
        self.update_call_btn.clicked.connect(self.update_call)

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
        groups = self.session.query(StudyGroup.id, StudyGroup.title).filter(department_id == department_id).all()

        for id, group in groups:
            self.group_box.addItem(str(id) + ": " + group)

    def get_current_group(self):

        return self.group_box.currentText()

    def get_current_department(self):

        return self.department_box.currentText()

    def next_key(self):

        all_id = [0]
        for st_id, d in self.student_id.items():
            for subj_id, grade in d.items():
                all_id.append(grade.id)

        return max(all_id) + 1

    def plot_grades(self):

        self.table.cellChanged.disconnect(self.change_grade)

        # clear
        self.student_id = dict()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)

        try:
            group_id = int(self.get_current_group().split(": ")[0])

            students = self.session.query(Student.id, Student.fcs).filter(Student.study_group_id == group_id).all()
            subjects = self.session.query(TheorySubject.id, TheorySubject.subject_name).all()
            grades = self.session.query(Grade).filter(Grade.student_id.in_([st.id for st in students])).all()

            for grade in grades:

                if grade.student_id not in self.student_id.keys():
                    self.student_id[grade.student_id] = dict()

                if grade.subject_id not in self.student_id[grade.student_id].keys():
                    self.student_id[grade.student_id][grade.subject_id] = grade

            self.table.setColumnCount(len(subjects))
            self.table.setRowCount(len(students))

            self.table.setHorizontalHeaderLabels([str(subjects[i][0]) + ": "
                                                + subjects[i][1] for i in range(0, len(subjects))])
            self.table.setVerticalHeaderLabels([str(students[i][0]) + ": "
                                              + students[i][1] for i in range(0, len(students))])

            for i, st in enumerate(students):
                st_id, student = st[0], st[1]

                for j, subj in enumerate(subjects):
                    subj_id, subject = subj[0], subj[1]

                    grade = "-"
                    if st_id in self.student_id.keys() and subj_id in self.student_id[st_id].keys():
                        grade = str(self.student_id[st_id][subj_id].grade_value)

                    self.table.setItem(i, j, QTableWidgetItem(str(grade)))

            self.table.resizeColumnsToContents()
        except:
            pass

        # reconnect to table
        self.table.cellChanged.connect(self.change_grade)

        pass

    def update_call(self):
        self.session.rollback()
        self.plot_grades()

    # signals
    def upgrade_db(self):

        def row2dict(row):
            d = {}
            for column in row.__table__.columns:
                d[column.name] = str(getattr(row, column.name))

            return d

        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Файл бэкапа')
        try:

            result = {}
            result[Grade.__tablename__] = [row2dict(row) for row in self.session.query(Grade).all()]
            with open(filename[0], 'w') as f:
                json.dump(result, f, default=str)

        except:

            ORMApplication.error("Ошибка при попытке сделать бэкап", "Введите другое имя", "Ошибка")

        self.plot_grades()

    def downgrade_db(self):

        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл бэкапа')
        try:
            with open(filename[0], 'r') as f:
                data = json.load(f)

                self.session.query(Grade).delete()

                for record in data[Grade.__tablename__]:
                    for k, v in record.items():
                        if v == 'None':
                            record[k] = None

                    data_obj = Grade(**record)
                    self.session.add(data_obj)

                self.session.commit()
        except:
            ORMApplication.error("Был выбран некорректный файл", "Выберите другой файл", "Ошибка")

        self.plot_grades()

    def update_department(self, s):

        self.update()
        self._init_group()

    def update_group(self, s):

        self.update()
        self.plot_grades()

    def update(self):

        try:
            self.session.commit()
        except BaseException as e:
            self.session.rollback()
            ORMApplication.error("Введена неверная оценка", "Введите корректное значение в поле оценки", "Ошибка")

    def change_grade(self, row, col):

        subj_id = int(self.table.horizontalHeaderItem(col).text().split(": ")[0])
        st_id = int(self.table.verticalHeaderItem(row).text().split(": ")[0])
        new_value = self.table.item(row, col).text()

        if st_id not in self.student_id.keys():
            self.student_id[st_id] = dict()

        try:
            if subj_id not in self.student_id[st_id].keys():
                grade = Grade()
                grade.id = self.next_key()
                grade.subject_id = subj_id
                grade.student_id = st_id

                self.student_id[st_id][subj_id] = grade

            self.student_id[st_id][subj_id].grade_value = int(new_value)
            self.session.add(self.student_id[st_id][subj_id])

        except BaseException as e:
            ORMApplication.error("Введена неверная оценка", "Введите корректное значение в поле оценки", "Ошибка")

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
