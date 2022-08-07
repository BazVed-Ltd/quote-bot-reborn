import pymongo
from typing import List

from quote_bot import db


async def insert_quote(quote: dict) -> dict:
    quote["id"] = await calculate_next_id(quote)
    await db.quotes.insert_one(quote)
    return quote


async def calculate_next_id(quote: dict) -> int:
    return await db.quotes.count_documents({"peer_id": quote["peer_id"]})


async def get_quote_by_id(peer_id: int, id: int) -> dict:
    return await db.quotes.find_one({"peer_id": peer_id, "id": id})


async def delete_quote_by_id(peer_id: int, id: int):
    last_quote = await get_last_quote(peer_id)

    if id < 0:
        id = last_quote["id"] + id + 1

    if last_quote["id"] == id:
        await db.quotes.delete_one({"_id": last_quote["_id"]})
        return
    else:
        await db.quotes.update_one({"id": id, "peer_id": peer_id}, {'$set': {'deleted': True}})


async def get_last_quote(peer_id: int) -> dict:
    return await db.quotes.find_one({"peer_id": peer_id}, sort=[("id", pymongo.DESCENDING)])


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
