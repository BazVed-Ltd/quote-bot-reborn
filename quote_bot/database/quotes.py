import pymongo
from typing import List

from quote_bot import db


async def insert_quote(quote: dict) -> dict:
    quote["id"] = await db.quotes.count_documents({})
    await db.quotes.insert_one(quote)
    return quote


async def get_quote_by_id(id: int) -> dict:
    return await db.quotes.find_one({"id": id})


async def delete_quote_by_id(id: int):
    last_quote = await get_last_quote()

    if id < 0:
        id = last_quote["id"] + id + 1

    if last_quote["id"] == id:
        await db.quotes.delete_one({"_id": last_quote["_id"]})
        return
    else:
        await db.quotes.update_one({"id": id}, {'$set': {'deleted': True}})


async def get_last_quote() -> dict:
    return await db.quotes.find_one(sort=[("id", pymongo.DESCENDING)])


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
