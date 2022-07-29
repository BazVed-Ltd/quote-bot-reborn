from vkbottle.bot import Bot, Message
from quote import Quote
from database import Database

from . import db, bot


# TODO: Не забыть про --deep
@bot.on.message(text="/сьлржалсч")
async def save_quote_handler(message: Message):
    quote = await Quote.from_message(message)
    db.add_quote(quote)
    return "ok"  # TODO: Нужно возвращать ссылку на сайт с цитатой
