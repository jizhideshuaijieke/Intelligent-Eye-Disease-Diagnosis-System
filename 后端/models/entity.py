from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship

from db.DB import Base


class Doctor(Base):
    __tablename__ = "doctor"

    accountId = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=True)
    age = Column(Integer, nullable=True)
    department = Column(String(50), nullable=True)
    photo = Column(MEDIUMTEXT, nullable=True)

    login = relationship("Logging", back_populates="doctor", uselist=False)


class Logging(Base):
    __tablename__ = "Logging"

    accountId = Column(Integer, ForeignKey("doctor.accountId"), primary_key=True, nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    password = Column(MEDIUMTEXT, nullable=True)

    doctor = relationship("Doctor", back_populates="login")


class CaseHistory(Base):
    __tablename__ = "Case_history"

    reportId = Column(String(50), primary_key=True, nullable=False)
    time = Column(String(50), nullable=True)
    outcome = Column(String(100), nullable=True)
    leftPhoto = Column(MEDIUMTEXT, nullable=True)
    rightPhoto = Column(MEDIUMTEXT, nullable=True)
    aiSuggestion = Column(MEDIUMTEXT, nullable=True)

    patient = relationship("Patient", back_populates="case_history", uselist=False)


class Patient(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=True)
    age = Column(Integer, nullable=True)
    reportId = Column(String(50), ForeignKey("Case_history.reportId"), nullable=False, unique=True)

    case_history = relationship("CaseHistory", back_populates="patient")
