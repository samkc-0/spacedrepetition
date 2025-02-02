from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from pydantic import model_validator
from sqlmodel import Field, SQLModel, Session, create_engine
from models import User, Word, Sentence, Memory
from parsers import seed_test_data

database_name = "database"
sql_url = f"sqlite:///{database_name}.db"
engine = create_engine(sql_url)


def get_session():
    with Session(engine) as session:
        yield session


def setup_database():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        test_data = seed_test_data()
        session.add(User(username="admin", password="password123"))
        session.add(User(username="superadmin", password="password123"))
        session.add_all(test_data["words"])
        session.add_all(test_data["sentences"])
        session.add_all(test_data["memories"])
        session.commit()


if __name__ == "__main__":
    setup_database()
