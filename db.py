from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from pydantic import model_validator
from sqlmodel import Field, SQLModel, Session, create_engine
from models import User, Word, Sentence, Memory

database_name = "database"
sql_url = f"sqlite:///{database_name}.db"
engine = create_engine(sql_url)


def setup_database():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    setup_database()
