from src import database
from src.config import load_config

config = load_config()
db = database.connect(config["quote"]["mongodb_uri"], config["quote"]["mongodb_db_name"])
