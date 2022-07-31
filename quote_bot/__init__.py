from quote_bot.database.connect import connect
from quote_bot.config import load_config

config = load_config()
db = connect(config["quote"]["mongodb_uri"], config["quote"]["mongodb_db_name"])
