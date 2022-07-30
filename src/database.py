import pymongo


def connect(db_uri: str, db_name: str):
    client = pymongo.MongoClient(db_uri)
    return client[db_name]
