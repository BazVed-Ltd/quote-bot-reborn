import os
from vkbottle import load_blueprints_from_package
from vkbottle.bot import Bot

from . import config
from .database.cache import bp as db_cache_bp, daily_recache

bot = Bot(token=config["vk_token"])

for bp in load_blueprints_from_package(os.path.normcase("quote_bot/commands")):
    bp.load(bot)

db_cache_bp.load(bot)
bot.loop.create_task(daily_recache())

bot.run_forever()
