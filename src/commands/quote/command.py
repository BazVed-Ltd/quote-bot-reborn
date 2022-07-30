from vkbottle.bot import Message, Blueprint
from .quote import Quote

from ... import db
from . import bp

# TODO: Не забыть про --deep
@bp.on.message(text="/сьлржалсч")
async def save_quote_handler(message: Message):
    quote = await Quote.from_message(message)
    db.add_quote(quote)
    # TODO: Нужно возвращать ссылку на сайт с цитатой
    return str(quote.clean_fields())
