import os

from vkbottle import load_blueprints_from_package

from . import bot

for bp in load_blueprints_from_package(os.path.normcase("src/commands")):
    bp.load(bot)

bot.run_forever()
