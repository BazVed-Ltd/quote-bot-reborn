from quote_bot import db


async def insert_chat(chat: dict):
    return await db.chats.insert_one(chat)

async def get_chat_by_id(chat_id: int) -> dict:
    return await db.chats.find_one({"id": chat_id})
