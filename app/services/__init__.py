from app.core.services import BaseService
from app.db import get_session
from app.models import Message, Thread, User

users = BaseService(User, get_session)
threads = BaseService(Thread, get_session)
messages = BaseService(Message, get_session)
