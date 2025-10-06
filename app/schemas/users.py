import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str
    username: str = Field(pattern="\w+")
    account_type: str


class UserResponse(BaseModel):
    id: str | uuid.UUID
    name: str
    username: str
    account_type: str


class ThreadCreate(BaseModel):
    title: str
    user_id: str | uuid.UUID


class ThreadResponse(BaseModel):
    id: str | uuid.UUID
    title: str
    user_id: str | uuid.UUID

    date_created: datetime
    last_updated: datetime


class CreateMessage(BaseModel):
    user_id: str | uuid.UUID
    thread_id: str | uuid.UUID
    content: str


class MessageResponse(BaseModel):
    id: str | uuid.UUID
    content: str
    user_id: str | uuid.UUID
    thread_id: str | uuid.UUID

    user: UserCreate

    date_created: datetime
    last_updated: datetime
