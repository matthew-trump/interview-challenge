from sqlalchemy import Column, Integer, String, DateTime, Table, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Symptom(Base):
    __tablename__ = "symptom"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    business_id  = Column(Integer, ForeignKey('business.id'),nullable=False)
    symptom_code = Column(String(9), ForeignKey('symptom_code.code'),nullable=False)
    symptom_diagnostic = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    business   = relationship('Business',foreign_keys="Symptom.business_id")
    symptom    = relationship('SymptomCode',foreign_keys="Symptom.symptom_code")


class Business(Base):
    __tablename__ = "business"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

class SymptomCode(Base):
    __tablename__ = "symptom_code"

    code = Column(String(9), primary_key=True, index=True)
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

