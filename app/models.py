from sqlalchemy import Column, Integer, String, DateTime, Table, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


business_symptom_association = Table(
    'business_symptom',
    Base.metadata,
    Column('business_id', Integer, ForeignKey('business.id')),
    Column('symptom_code', String, ForeignKey('symptom.code')),
    Column('diagnostic', Boolean, nullable=False),
    Column('created_at',DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow),
    Column('updated_at',DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow),
    Column('created_by',String(100), nullable=True),
    Column('updated_by',String(100), nullable=True)

    
)

class Business(Base):
    __tablename__ = "business"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(100), nullable=False)
    symptoms = relationship("Symptom", secondary=business_symptom_association)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

class Symptom(Base):
    __tablename__ = "symptom"

    code = Column(String, primary_key=True, index=True)
    name = Column(String)
    businesses = relationship("Business", secondary=business_symptom_association)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

