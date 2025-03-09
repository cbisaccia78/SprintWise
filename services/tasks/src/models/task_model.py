from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func

from src.database import db

class Task(db.Model):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(String(50), default='To Do')
    estimated_time = Column(Float, default=0.0)
    assigned_user = Column(String(255), default="unassigned")
    priority = Column(String(7), default='Medium')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<Task {self.title}>'