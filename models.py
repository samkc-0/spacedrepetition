from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from password import get_password_hash


class Answer(BaseModel):
    memory_id: int
    correct: bool
    extra: Optional[str] = None


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, **data: Any):
        data["password"] = get_password_hash(data["password"])
        super().__init__(**data)


class Memory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    word_id: int
    user_id: int
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_review: Optional[datetime] = None


class Word(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str = Field(index=True)
    meaning: Optional[str] = None
    state: int = Field(index=True)
    frequency: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Sentence(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    word_id: int
    text: str
    level: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Question(SQLModel):
    memory: Memory
    word: Word
    sentence: Sentence
