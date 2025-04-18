import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQL_SERVER_DATABASE_URL = 'mssql+pymssql://testadmin:Mosu!123@sqlserver-raj.c6um8x5yb22t.us-east-1.rds.amazonaws.com/ViziApps'

engine = create_engine(SQL_SERVER_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
