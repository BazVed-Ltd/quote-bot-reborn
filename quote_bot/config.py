from os import getenv

def load_config():
    config = {"quote": {}}
    config["quote"]["vk_token"] = getenv("VK_TOKEN")
    config["quote"]["mongodb_uri"] = getenv("MONGODB_URI") or "mongodb://mongodb:mongodb@mongodb:27017"
    config["quote"]["mongodb_db_name"] = getenv("MONGODB_DB_NAME") or "quote_dev"
    return config
