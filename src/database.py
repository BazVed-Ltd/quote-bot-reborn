import pymongo

from .commands.quote.quote import Quote


class Database():
    def __init__(self, db_uri: str, db_name: str = "quote_dev"):
        self.client = pymongo.MongoClient(db_uri)
        self.db = self.client[db_name]

        self.quotes = self.db.quotes

    def add_quote(self, quote: Quote) -> None:
        quote.id = self.quotes.count_documents({})
        return self.quotes.insert_one(quote.clean_fields())

    def get_quote_by_id(self, id) -> Quote:
        quote = self.db.quotes.find_one({"id": id})
        if quote:
            return Quote.from_dict(quote)
        return None
