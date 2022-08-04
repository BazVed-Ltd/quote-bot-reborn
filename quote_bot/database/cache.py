import asyncio
from types import SimpleNamespace
from typing import List
from os import remove
import logging

from quote_bot import db
from quote_bot.database.quotes import get_unique_ids
from quote_bot.utils import download_attachment_by_url, save_attachment_bytes_to_disk

from vkbottle.bot import Blueprint

bp = Blueprint("DatabaseCache")

logger = logging.getLogger("db_cache")


async def users_groups_get(ids: List[int]) -> List[SimpleNamespace]:
    group_ids = []
    user_ids = []
    for _id in ids:
        if _id > 0:
            user_ids.append(_id)
        else:
            group_ids.append(abs(_id))

    users = []
    if len(user_ids) != 0:
        for user in await bp.api.users.get(user_ids, fields=["photo_200"]):
            if user.deactivated is not None:
                continue
            users.append(SimpleNamespace(name=f"{user.first_name} {user.last_name}",
                                         photo_200=user.photo_200,
                                         id=user.id,
                                         is_user=True))
    groups = []
    if len(group_ids) != 0:
        for group in await bp.api.groups.get_by_id(group_ids, fields=["photo_200"]):
            if group.deactivated is not None:
                continue
            groups.append(SimpleNamespace(name=group.name,
                                          photo_200=group.photo_200,
                                          id=-group.id,
                                          is_user=False))
    return users + groups


async def update():
    prev_state = await db.cache_state.find_one()
    unique_ids = set(await get_unique_ids())
    new_ids = unique_ids - set(prev_state["unique_ids"])
    new_users = await users_groups_get(new_ids)
    for user in new_users:
        pic_bytes = await download_attachment_by_url(user.photo_200)
        pic_filepath = save_attachment_bytes_to_disk(pic_bytes)
        await db.cache.insert_one({
            "id": user.id,
            "name": user.name,
            "pic": pic_filepath
        })


async def daily_recache():
    prev_state = await db.cache_state.find_one()
    if prev_state is None:
        prev_state = {"last_checked": 0, "unique_ids": []}
        await db.cache_state.insert_one(prev_state)
    while True:
        logger.info("Running full recache...")
        users = dict([(user.id, {"name": user.name, "photo_200": user.photo_200}) for user in await users_groups_get(await get_unique_ids())])
        for user in users:
            user_in_db = dict(await db.cache.find_one({"id": user}))
            user_in_db["name"] = users[user]["name"]
            pic_bytes = await download_attachment_by_url(users[user]["photo_200"])
            pic = save_attachment_bytes_to_disk(pic_bytes)
            if user_in_db["pic"] != pic:
                remove(user_in_db["pic"])
                user_in_db["pic"] = pic
            await db.cache.replace_one({"id": user}, user_in_db)
        await asyncio.sleep(86_400)
