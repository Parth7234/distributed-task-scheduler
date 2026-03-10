from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    priority = Column(Integer, index=True)
    description = Column(String)
    status = Column(String, default="PENDING")
    started_at = Column(DateTime, nullable=True)# nullable=True when the task is just PENDING
    result = Column(String, nullable=True)