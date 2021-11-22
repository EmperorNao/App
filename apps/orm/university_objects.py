from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
Base = declarative_base()


class Department(Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String, nullable=False)


class Professor(Base):
    __tablename__ = "professor"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'))
    age = Column(Integer, nullable=False)
    fcs = Column(String, nullable=False)
    prof_status = Column(String, nullable=False)
    experience = Column(Integer, nullable=False)


class StudyGroup(Base):
    __tablename__ = "study_group"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'))
    title = Column(String, nullable=False)
    spec_code = Column(String, nullable=False)


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    study_group_id = Column(Integer, ForeignKey('study_group_id.id'))
    fcs = Column(String, nullable=False)
    age = Column(Integer, nullable=False)


class TheorySubject(Base):
    __tablename__ = "theory_subject"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    subject_name = Column(String, nullable=False)


class Audience(Base):
    __tablename__ = "audience"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)


class Grade(Base):
    __tablename__ = "grade"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    subject_id = Column(Integer, ForeignKey('theory_subject.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    professor_id = Column(Integer, ForeignKey('professor.id'))
    grade_value = Column(Integer, nullable=False)


class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    professor_id = Column(Integer, ForeignKey('professor.id'))
    subject_id = Column(Integer, ForeignKey('theory_subject.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('study_group.id'), nullable=False)
    audience_id = Column(Integer, ForeignKey('audience.id'))
    event_time = Column(DateTime, nullable=False)


def OrmFactory(s):
    if s == "Class":
        return Class
    elif s == "Grade":
        return Grade
    elif s == "Audience":
        return Audience
    elif s == "TheorySubject":
        return TheorySubject
    elif s == "Student":
        return Student
    elif s == "Professor":
        return Professor
    elif s == "StudyGroup":
        return StudyGroup
    elif s == "Department":
        return Department
    else:
        raise ValueError(f"Wrong str {s} was provided in OrmFactory")


def class_to_columns(s):
    if s == "Class":
        return ["professor_id", "subject_id", "group_id", "audience_id", "event_time"]
    elif s == "Grade":
        return ["subject_id", "student_id", "professor_id", "grade_value"]
    elif s == "Audience":
        return ["name", "floor"]
    elif s == "TheorySubject":
        return ["subject_name"]
    elif s == "Student":
        return ["study_group_id", "fcs", "age"]
    elif s == "Professor":
        return ["department_id", "age", "fcs", "prof_status", "experience"]
    elif s == "StudyGroup":
        return ["department_id", "title", "spec_code"]
    elif s == "Department":
        return ["title"]
    else:
        raise ValueError(f"Wrong str {s} was provided in class to column")

