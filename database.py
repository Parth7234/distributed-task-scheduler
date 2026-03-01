from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#define the connection URL
SQLALCHEMY_DATABASE_URL = "postgresql://localhost/task_scheduler"

#create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#create a Base class
Base = declarative_base()

#dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()