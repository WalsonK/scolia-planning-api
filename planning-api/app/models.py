from pydantic import BaseModel
from typing import List
from sqlalchemy import (Column, Integer, String, DateTime, func, Boolean, Enum,
                        Float, Date, Time, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

class Subject(BaseModel):
    name: str
    teacher: str
    hours_todo: float
    hours_total: float
    unavailable_periods: List[int]

    def create_empty(self):
        return Subject(name="empty", teacher="", hours_todo=0.0, hours_total=0.0, unavailable_periods=[])

class Room(BaseModel):
    name: str
    capacity: int

class Params(BaseModel):
    class_name: str
    slots_per_day: int
    days_per_week: int
    max_hours_per_week: int

class PlanningData(BaseModel):
    params: Params
    subjects: List[Subject]
    rooms: List[Room]


Base = declarative_base()

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    subjects = relationship("Subject", back_populates="teacher")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    coefficient = Column(Float, nullable=True)
    ects = Column(Float, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teacher", back_populates="subjects")
    class_info = relationship("Class", back_populates="subjects")
    # CORRECTION: Ajout de la relation inverse vers Document
    documents = relationship("Document", back_populates="subject")