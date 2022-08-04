from vkbottle.bot import Message, Blueprint
from vkbottle.dispatch.rules.base import RegexRule

from quote_bot.rules import NameArguments
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
        result["fwd_messages"] = [await fwd_message_to_dict(msg, from_reply=inner_from_reply, deep=deep-1) for msg in get_fwd_messages(message)]
    else:
        result["fwd_messages"] = []

    result["attachments"] = [await attachment_to_dict(attachment) for attachment in message.attachments]
    return result


@bp.on.message(NameArguments("deep", "d"), RegexRule("^/сьлржалсч"))
async def save_quote_handler(message: Message, deep: str, d: str):
    try:
        quote_deep = int(deep or d or -1)
        if not (quote_deep >= 0 or quote_deep == -1):
            raise ValueError
    except ValueError:
        return "Глубинность должна быть ЧИСЛОМ >= 0 или -1"

    if not message.fwd_messages and not message.reply_message:
        return "И че сохранить-то надо"

    quote = await message_to_dict(message, deep=quote_deep)

    quote = quotes_db.insert_quote(quote)

    await db_cache.update()

    return str(quote["id"])  # TODO: Нужно возвращать ссылку на сайт с цитатой

# TODO: Реализовать как в оригинале. На данный момент нужен для разработки


@bp.on.message(NameArguments("j"), RegexRule("^/сь"))
async def save_quote_handler(message: Message, j=None):
    if j:
        return str(quotes_db.get_quote_by_id(int(j)))
    return "Ещё не готово, используй -j"

