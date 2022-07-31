from quote_bot import db


def insert_quote(quote: dict) -> dict:
    quote["id"] = db.quotes.count_documents({}) # FIXME при удалении цитат айдишники будут неправильные
    db.quotes.insert_one(quote)
    return quote

def get_quote_by_id(id: int) -> dict:
    return db.quotes.find_one({"id": id})
        