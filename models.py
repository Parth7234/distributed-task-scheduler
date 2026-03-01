from sqlalchemy import Column, Integer, String
from database import Base

class Task(Base):

    __tablename__ = "tasks"

    # define columns for table
    id = Column(Integer, primary_key=True, index=True)
    priority = Column(Integer, index=True)  
    description = Column(String)
    status = Column(String, default="PENDING")