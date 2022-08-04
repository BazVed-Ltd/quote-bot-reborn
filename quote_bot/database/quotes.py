from typing import List

from quote_bot import db


async def insert_quote(quote: dict) -> dict:
    quote["id"] = await db.quotes.count_documents({})  # FIXME при удалении цитат айдишники будут неправильные
    await db.quotes.insert_one(quote)
    return quote


async def get_quote_by_id(id: int) -> dict:
    return await db.quotes.find_one({"id": id})


async def get_unique_ids() -> List[int]:
    state = await db.cache_state.find_one()

    state["unique_ids"] = set(state["unique_ids"])

    def process_message(quote: dict):
        state["unique_ids"].add(quote["from_id"])
        for fwd_msg in quote["fwd_messages"]:
            process_message(fwd_msg)

    async for quote in db.quotes.find(skip=state["last_checked"]):
        process_message(quote)
        state["last_checked"] = max(state["last_checked"], quote["id"])

    state["unique_ids"] = list(state["unique_ids"])
    await db.cache_state.replace_one({}, state)

    return state["unique_ids"]
