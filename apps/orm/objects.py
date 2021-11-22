from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

Base = declarative_base()


class Department(Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    title = Column(String, not_null=True)


class Professor(Base):
    __tablename__ = "professor"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    department_id = Column(Integer, ForeignKey('department.id'))
    age = Column(Integer, not_null=True)
    fcs = Column(String, not_null=True)
    prof_status = Column(String, not_null=True)
    experience = Column(Integer, not_null=True)


class StudyGroup(Base):
    __tablename__ = "study_group"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    department_id = Column(Integer, ForeignKey('department.id'))
    title = Column(String, not_null=True)
    spec_code = Column(String, not_null=True)


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    study_group_id = Column(Integer, ForeignKey('study_group_id.id'))
    fcs = Column(String, not_null=True)
    age = Column(Integer, not_null=True)


class TheorySubject(Base):
    __tablename__ = "theory_subject"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    subject_name = Column(String, not_null=True)


class Audience(Base):
    __tablename__ = "audience"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    name = Column(String, not_null=True)
    floor = Column(Integer, not_null=True)


class Grade(Base):
    __tablename__ = "grade"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    subject_id = Column(Integer, ForeignKey('theory_subject.id'), not_null=True)
    student_id = Column(Integer, ForeignKey('student.id'), not_null=True)
    professor_id = Column(Integer, ForeignKey('professor.id'))
    grade_value = Column(Integer, not_null=True)


class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True, autoincrement=True, not_null=True)
    professor_id = Column(Integer, ForeignKey('professor.id'))
    subject_id = Column(Integer, ForeignKey('theory_subject.id'), not_null=True)
    group_id = Column(Integer, ForeignKey('study_group.id'), not_null=True)
    audience_id = Column(Integer, ForeignKey('audience.id'))
    event_time = Column(DateTime, not_null=True)
