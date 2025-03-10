import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


DATABASE_URI = os.environ['DATABASE_URL']
DATABASE_URI = DATABASE_URI.replace("postgres", "postgresql")

try:
  engine = create_engine(DATABASE_URI)
except Exception as e:
  print('An exception occurred while creating database connection')
  print(e)
  SQLALCHEMY_DATABASE_URL = 'sqlite:///./blog.db'
  engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.model.model import Base  # Import your models here

# Create tables
Base.metadata.create_all(engine)


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


class DBSession:

  def __init__(self):
    self.session = None

  def __enter__(self):
    self.session = SessionLocal()
    return self.session

  def __exit__(self, exc_type, exc_value, traceback):
    self.session.close()
