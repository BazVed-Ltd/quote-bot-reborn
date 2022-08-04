import pymongo
import signal
import sys

def connect(db_uri: str, db_name: str):
    client = pymongo.MongoClient(db_uri)
    def disconnect(sig, frame):
        client.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, disconnect)

    return client[db_name]
