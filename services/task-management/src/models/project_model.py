from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from src.database import db

class Project(db.Model):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tasks = relationship('Task', backref=backref('project', lazy='joined'))