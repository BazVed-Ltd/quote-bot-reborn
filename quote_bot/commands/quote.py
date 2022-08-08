from typing import Optional
from vkbottle.bot import Message, Blueprint

from quote_bot.rules import NamedArguments, Argument, command_regex
from quote_bot.database import quotes as quotes_db
from quote_bot.database import cache as db_cache
from quote_bot.utils import *

bp = Blueprint("Quotes")

QUOTES_VERSION = 1


async def message_to_dict(message: Message, deep: int = -1) -> dict:
    result = {}
    result["date"] = message.date
    result["peer_id"] = message.peer_id
    result["from_id"] = message.from_id
    result["version"] = QUOTES_VERSION

    from_reply = bool(message.reply_message)

    result["fwd_messages"] = [await fwd_message_to_dict(msg, from_reply=from_reply, deep=deep) for msg in get_fwd_messages(message)]
    return result


async def fwd_message_to_dict(message: Message, from_reply=False, deep: int = -1) -> dict:
    if from_reply:
        messages = await bp.api.messages.get_by_id(message_ids=[message.id])
        message = messages.items[0]
    result = {}
    result["from_id"] = message.from_id
    result["date"] = message.date
    result["text"] = message.text

    inner_from_reply = bool(message.reply_message)

    if deep != 0:
        result["fwd_messages"] = [await fwd_message_to_dict(msg, from_reply=inner_from_reply, deep=deep - 1) for msg in get_fwd_messages(message)]
    else:
        result["fwd_messages"] = []

    result["attachments"] = [await attachment_to_dict(attachment) for attachment in message.attachments]
    return result


@bp.on.message(
    command_regex("сьлржалсч"),
    NamedArguments(
        Argument(name="deep", shortname="d"),
        Argument(name="глубинность", shortname="г", in_command_name="deep")
    )
)
async def save_quote_handler(message: Message, deep: Optional[str] = None):
    try:
        quote_deep = int(deep or -1)
        if not (quote_deep >= 0 or quote_deep == -1):
            raise ValueError
    except ValueError:
        return "Глубинность должна быть ЧИСЛОМ >= 0 или -1"

    if not message.fwd_messages and not message.reply_message:
        return "И че сохранить-то надо"

    quote = await message_to_dict(message, deep=quote_deep)

    quote = await quotes_db.insert_quote(quote)

    await db_cache.update()

    return str(quote["id"])  # TODO: Нужно возвращать ссылку на сайт с цитатой


@bp.on.message(
    command_regex("сь"),
    NamedArguments(
        Argument(name="dev", shortname="d"),
        Argument(name="deleted", shortname="D", is_flag=True)
    )
)
async def get_quote_handler(message: Message, dev: Optional[str] = None, deleted: Optional[bool] = False):
    # TODO: Реализовать как в оригинале. На данный момент нужен для разработки.
    if dev:
        quote = await quotes_db.get_quote_by_id(message.peer_id, int(dev))
        if not quote or quote.get("deleted", False) and not deleted:
            return "ИндексОшибка: индекс списка вышел из области"
        return str(quote)
    return "Ещё не готово, используй -d"


@bp.on.message(command_regex("сьдел"))
async def delete_quote_handler(message: Message):
    args = message.text.split()[1:]
    if len(args) != 1:
        return "Спок, нужен только ОДИН аргумент - айди цитаты"
    quote_id = int(args[0])

    await quotes_db.delete_quote_by_id(message.peer_id, quote_id)
    return "Понял"
