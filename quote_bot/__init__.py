from quote_bot.database.connect import connect
from quote_bot.config import load_config

config = load_config()
db = connect(config["mongodb_uri"], config["mongodb_db_name"])
