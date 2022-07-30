import os
import importlib

from . import bot

for command in os.listdir("src/commands"):
    if command.startswith("_"):
        continue
    command = command.removesuffix(".py")

    command = importlib.import_module(f".commands.{command}", "src")
    command.bp.load(bot)

bot.run_forever()
