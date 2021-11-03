import sys
from db.config import Config
from db.db import Database
from apps.console import ConsoleApplication
from apps.gui import GUIApplication
from PyQt5 import QtWidgets
import pymysql


if __name__ == "__main__":

    database_name = "university"
    try:
        config = Config(db_name=database_name)
        database = Database(config)
    except pymysql.err.OperationalError:
        print("Unable to make a connection to the mysql database with name '%s'" % database_name)
        exit(0)

    tables = ["audience", "class", "department", "grade", "professor", "student", "study_group", "theory_subject"]

    queries = {"Все студенты и их оценки": "select st.fcs, p.fcs, g.grade_value from grade as g \
                inner join student as st \
                on st.id = g.student_id \
                inner join professor as p \
                on p.id = g.professor_id",

               "Количество должников по кафедрам": "select department.title as 'Кафедра', \
               count(distinct(student_id)) as 'Количество должников' from grade \
                inner join student \
                on grade.student_id = student.id \
                inner join study_group \
                on student.study_group_id = study_group.id \
                inner join department \
                on department.id = study_group.department_id \
                where grade_value < 3 \
                group by department_id",

               "Процент остепенённости преподаваталей по кафедрам": "select department_id as \
               dep_num, department.title as 'Кафедра', \
               (select count(*) from professor where department_id = dep_num and prof_status != '') / \
               (select count(*) from professor where department_id = dep_num) \
               * 100 as 'Процент остепенённых' from professor \
                inner join department \
                on professor.department_id = department.id \
                group by department_id"

               }

    if len(sys.argv) > 1 and sys.argv[1] == "console":
        app = ConsoleApplication(database, tables, queries)
        app.run()

    elif len(sys.argv) > 1 and sys.argv[1] == "GUI":

        app = QtWidgets.QApplication(sys.argv)
        model = GUIApplication(database, tables, queries)
        model.show()
        sys.exit(app.exec_())

    else:
        print("Provide one of arguments:\n'console' - console app\n'GUI' - with graphical interface")
