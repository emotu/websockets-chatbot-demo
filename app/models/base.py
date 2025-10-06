import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass


class User(SQLModel, table=True):
    """User Table"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(nullable=False, unique=True, index=True)

    name: str
    account_type: str = Field(default="user", nullable=False)

    date_created: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, default=func.now()),
    )
    last_updated: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        ),
    )

    messages: list["Message"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Thread(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    user_id: uuid.UUID = Field(foreign_key="user.id", default_factory=uuid.uuid4)

    date_created: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, default=func.now()),
    )
    last_updated: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        ),
    )


class Participant(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(foreign_key="user.id")
    thread_id: uuid.UUID = Field(foreign_key="thread.id")
    role: str | None = Field(default="owner")

    date_created: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, default=func.now()),
    )
    last_updated: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        ),
    )


class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(
        back_populates="messages", sa_relationship_kwargs={"lazy": "selectin"}
    )
    content: str

    status: str | None = Field(default="read")  # SENT ...
    thread_id: uuid.UUID = Field(foreign_key="thread.id")

    date_created: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, default=func.now()),
    )
    last_updated: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        ),
    )
