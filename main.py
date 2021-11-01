# This is a sample Python script.

import sys
from ConsoleApp import ConsoleApplication
from config import Config
from DB import Database

r"""
command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)
"""


if __name__ == "__main__":

    config = Config(db_name="university")
    database = Database(config)
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
               Номер_кафедры, department.title as 'Кафедра', \
               (select count(*) from professor where department_id = Номер_кафедры and prof_status != '') \
               (select count(*) from professor where department_id = Номер_кафедры) \
               * 100 as 'Процент остепенённых ' from professor \
                inner join department \
                on professor.department_id = department.id \
                group by department_id"
               
               }

    if len(sys.argv) < 2 or sys.argv[1] == "console":
        App = ConsoleApplication(database, tables, queries)

    else:
        # TODO GUI
        pass

    App.run()

