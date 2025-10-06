import asyncio
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from rich.pretty import pprint

from app.agents.runner import writer_agent
from app.core.dispatcher import DispatchManager
from app.core.exceptions import (
    ServiceError,
    http_exception_handler,
    service_error_handler,
    validation_error_handler,
)
from app.db import init_db
from app.models import Message, Thread
from app.schemas.users import (
    CreateMessage,
    MessageResponse,
    ThreadCreate,
    ThreadResponse,
    UserCreate,
    UserResponse,
)
from app.services import messages, threads, users

load_dotenv()

dispatcher = DispatchManager(writer_agent)


@asynccontextmanager
async def lifespan(app):
    """
    Lifespan manager
    """
    await init_db()
    await dispatcher.start()
    yield


app = FastAPI(lifespan=lifespan)

# Register exception handlers
app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_error_handler)

# Override FastAPI's built-in validation error handler
app.add_exception_handler(RequestValidationError, validation_error_handler)


@app.get("/")
async def index():
    return dict(name="Writer AI", version="1.0.0")


@app.get("/users", response_model=list[UserResponse])
async def list_users():
    user_list = await users.list()
    return user_list


@app.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int | str | uuid.UUID):
    user = await users.get(id)
    return user


@app.get("/threads", response_model=list[ThreadResponse])
async def list_threads():
    thread_list = await threads.list()
    return thread_list


@app.get("/users/{user_id}/threads", response_model=list[ThreadResponse])
async def get_user_threads(user_id: uuid.UUID):
    thread_list = await threads.filter(Thread.user_id == user_id)
    return thread_list


@app.get("/threads/{thread_id}/messages", response_model=list[MessageResponse])
async def get_thread_messages(thread_id: uuid.UUID):
    message_list = await messages.filter(Message.thread_id == thread_id)
    return message_list


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(input: UserCreate):
    obj = await users.create(input.model_dump())
    return obj


@app.post(
    "/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED
)
async def create_thread(input: ThreadCreate):
    obj = await threads.create(input.model_dump())

    return obj


@app.post(
    "/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(input: CreateMessage):
    obj = await messages.create(input.model_dump())
    await dispatcher.receive(obj.thread_id, obj.id)

    return obj


@app.websocket("/ws/{thread_id}")
async def connect(websocket: WebSocket, thread_id: uuid.UUID):
    await websocket.accept()
    queue = await dispatcher.connect(thread_id)
    try:
        while True:
            thread_id, reply = await queue.get()
            await websocket.send_text(reply)

    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        await websocket.close(code=1001)
        raise
    except Exception as e:
        pprint(e)
        await websocket.close(code=1011)
    finally:
        print("cleaning up")
        await websocket.close(code=1001)
        raise
