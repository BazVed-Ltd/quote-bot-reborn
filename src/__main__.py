from .config import config
from .database import Database
from vkbottle.bot import Bot

bot = Bot(token=config["quote"]["vk_token"])
db = Database(config["quote"]["mongodb_uri"])

bot.run_forever()