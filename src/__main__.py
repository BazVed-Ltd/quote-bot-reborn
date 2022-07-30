import os
from vkbottle import load_blueprints_from_package
from vkbottle.bot import Bot

from . import config

bot = Bot(token=config["quote"]["vk_token"])

for bp in load_blueprints_from_package(os.path.normcase("src/commands")):
    bp.load(bot)

bot.run_forever()
