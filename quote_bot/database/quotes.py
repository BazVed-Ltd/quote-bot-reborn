from typing import List

from quote_bot import db


def insert_quote(quote: dict) -> dict:
    quote["id"] = db.quotes.count_documents({}) # FIXME при удалении цитат айдишники будут неправильные
    db.quotes.insert_one(quote)
    return quote

def get_quote_by_id(id: int) -> dict:
    return db.quotes.find_one({"id": id})

def get_unique_ids() -> List[int]:
    state = db.cache_state.find_one()

    state["unique_ids"] = set(state["unique_ids"])
    def process_message(msg: dict):
        state["unique_ids"].add(msg["from_id"])
        for fwd_msg in msg["fwd_messages"]:
            process_message(fwd_msg)
    for quote in db.quotes.find(skip=state["last_checked"]):
        process_message(quote)
        state["last_checked"] = quote["id"]

    state["unique_ids"] = list(state["unique_ids"])
    db.cache_state.replace_one({}, state)

    return state["unique_ids"]