from typing import Optional
from vkbottle.bot import Message, Blueprint

from quote_bot.rules import NamedArguments, Argument, command_regex
from quote_bot.database import chats as chats_db
from quote_bot.utils import *

bp = Blueprint("Chats")


async def chat_from_message(message: Message, **kwargs):
    chat = {"id": message.peer_id}

    chat_from_vk = None

    async def get_chat_from_vk():
        nonlocal chat_from_vk

        if chat_from_vk:
            return chat_from_vk

        response = await bp.api.messages.get_conversations_by_id(peer_ids=[chat["id"]])
        try:
            chat_from_vk = response.items[0]
        except IndexError:
            message = "Укажите аргумент --название или дайте права администратора"
            raise CommandArgumentError(message)
        return chat_from_vk

    if kwargs.get("chat_name"):
        chat["name"] = kwargs["chat_name"]
    else:
        chat["name"] = (await get_chat_from_vk()).chat_settings.title

    return chat


@bp.on.chat_message(
    command_regex("инит"),
    NamedArguments(Argument(name="название", in_command_name="chat_name"))
)
async def save_quote_handler(message: Message, chat_name: Optional[str] = None):
    chat_in_db = await chats_db.get_chat_by_id(message.peer_id)
    if chat_in_db:
        return str(chat_in_db) # TODO: Красивый принт

    try:
        chat = await chat_from_message(message, chat_name=chat_name)
    except CommandArgumentError as e:
        return str(e)

    await chats_db.insert_chat(chat)
    return str(chat) # TODO: Красивый принт
