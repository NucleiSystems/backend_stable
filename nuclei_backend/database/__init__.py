import pathlib
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

path = pathlib.Path(__file__).parent.absolute()


SQLALCHEMY_DATABASE_URI1 = "postgresql://postgres:postgrespw@localhost:5432"
SQLALCHEMY_DATABASE_URI2 = "postgresql://postgres:postgrespw@postgres:5432"
SQLALCHEMY_DATABASE_URI3 = "postgresql://postgres:postgrespw@host.docker.internal:5432"


engine = create_engine(
    environ.get("DATABASE_URL"),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
