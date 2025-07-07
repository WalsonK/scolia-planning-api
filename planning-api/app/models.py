from pydantic import BaseModel
from typing import List
from sqlalchemy import (Column, Integer, String, DateTime, func, Boolean, Enum,
                        Float, Date, Time, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
import enum

class UserRole(str, enum.Enum):
    """
    Énumération pour les rôles utilisateur.
    Hérite de 'str' pour être facilement sérialisable en JSON.
    """
    STUDENT = "etudiant"
    TEACHER = "professeur"
    MANAGER = "gestionnaire"

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

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    myges_username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation: Un utilisateur peut avoir plusieurs inscriptions (une par classe/année)
    enrollments = relationship("Enrollment", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"

# --- NOUVEAUX MODÈLES ACADÉMIQUES ---

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False, index=True)
    email = Column(String, index=True, nullable=True)
    subjects = relationship("Subject", back_populates="teacher")

class AcademicYear(Base):
    __tablename__ = "academic_years"
    id = Column(Integer, primary_key=True, index=True)
    year_label = Column(String, unique=True, nullable=False)
    documents = relationship("Document", back_populates="academic_year")

class Major(Base):
    __tablename__ = "majors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    short_name = Column(String, unique=True, nullable=False)

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, nullable=False)
    group = Column(Integer, nullable=False)
    year_id = Column(Integer, ForeignKey("academic_years.id"))
    major_id = Column(Integer, ForeignKey("majors.id"))
    subjects = relationship("Subject", back_populates="class_info")
    academic_year = relationship("AcademicYear")

    major = relationship("Major")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    user = relationship("User", back_populates="enrollments")

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

class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    grade_type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))

class Absence(Base):
    __tablename__ = "absences"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    absence_type = Column(String, nullable=True)
    is_justified = Column(Boolean, default=False)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))

class Document(Base):
    """Représente un document téléchargé."""
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    
    display_name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    document_type = Column(String, nullable=False)
    
    last_modified_on_myges = Column(String, nullable=False)
    download_url = Column(String, nullable=False)
    
    local_path = Column(String, nullable=True)
    file_extension = Column(String, nullable=True)
    
    level = Column(Integer, nullable=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # CORRECTION: Ajout des relations manquantes
    academic_year = relationship("AcademicYear", back_populates="documents")
    subject = relationship("Subject", back_populates="documents")