import asyncio
from typing import List, Dict, Union
from os import remove
import logging

from quote_bot import db
from quote_bot.database.quotes import get_unique_ids
from quote_bot.utils import download_attachment_by_url, save_attachment_bytes_to_disk

from vkbottle.bot import Blueprint

bp = Blueprint("DatabaseCache")

logger = logging.getLogger('db_cache')

async def users_groups_get(ids: List[int]) -> List[Dict[str, Union[str, int]]]:
    group_ids = []
    user_ids = []
    for _id in ids:
        if _id > 0:
            user_ids.append(_id)
        else:
            group_ids.append(abs(_id))
    users = [{
            "name": f"{user.first_name} {user.last_name}",
            "photo_200": user.photo_200,
            "id": user.id,
            "group": "first_name" in user
        } for user in await bp.api.users.get(user_ids, fields=['photo_200'])] if len(user_ids) != 0 else [] + \
        await bp.api.groups.get_by_id(group_ids, fields=['photo_200']) if len(group_ids) != 0 else []
    return users

async def update():
    prev_state = db.cache_state.find_one()    
    unique_ids = set(get_unique_ids())
    new_ids = unique_ids - set(prev_state["unique_ids"])
    new_users = await users_groups_get(new_ids)
    for user in new_users:
        pic_bytes = await download_attachment_by_url(user['photo_200'])
        pic_filepath = save_attachment_bytes_to_disk(pic_bytes)
        db.cache.insert_one({
            'id': -user['id'] if user['group'] else user['id'],
            'name': user['name'],
            'pic': pic_filepath
        })

async def daily_recache():
    prev_state = db.cache_state.find_one()
    if prev_state is None:
        prev_state = {"last_checked": 0, "unique_ids": []}
        db.cache_state.insert_one(prev_state)
    while True:
        logger.info('Running full recache...')
        users = dict([(user['id'], {'name': user['name'], 'photo_200': user['photo_200']}) for user in await users_groups_get(get_unique_ids())])
        for user in users:
            user_in_db = dict(db.cache.find_one({'id': user}))
            user_in_db['name'] = users[user]['name']
            pic_bytes = await download_attachment_by_url(users[user]['photo_200'])
            users[user]['pic'] = save_attachment_bytes_to_disk(pic_bytes)
            if user_in_db['pic'] != users[user]['pic']:
                remove(user_in_db['pic'])
                user_in_db['pic'] = users[user]['pic']
            db.cache.replace_one({'id': user}, user_in_db)
        await asyncio.sleep(86_400)