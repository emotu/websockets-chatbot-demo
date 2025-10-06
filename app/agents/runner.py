from dotenv import load_dotenv
from rich.pretty import pprint
from writerai import Writer

from app.models import Message
from app.schemas.users import CreateMessage
from app.services import messages

load_dotenv()

client = Writer()

AGENT_ID = "65c4b7e8-4e05-4c31-b880-43bdd254f048"


async def writer_agent(dispatcher, thread_id, message_id):
    message = await messages.get(message_id)
    thread_messages = await messages.filter(Message.thread_id == message.thread_id)

    conversation = [
        dict(content=m.content, role=m.user.account_type) for m in thread_messages
    ]
    response = client.chat.chat(
        messages=conversation,
        model="palmyra-x5",
    )

    reply = response.choices[0].message.content

    payload = CreateMessage(user_id=AGENT_ID, thread_id=thread_id, content=reply)
    response = await messages.create(payload.model_dump())

    content = response.content
    pprint(content)

    await dispatcher.send(thread_id, content)
