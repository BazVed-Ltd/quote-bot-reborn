from os import getenv
from dotenv import load_dotenv

def load_config():
    load_dotenv("config.env")
    config = {}
    config["vk_token"] = getenv("VK_TOKEN")
    config["mongodb_uri"] = getenv("MONGODB_URI") or "mongodb://mongodb:mongodb@mongodb:27017"
    config["mongodb_db_name"] = getenv("MONGODB_DB_NAME") or "quote_dev"
    return config
