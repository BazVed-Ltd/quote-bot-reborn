from quote_bot import db
from quote_bot.database.quotes import get_unique_ids
from quote_bot.utils import download_attachment_by_url, save_attachment_bytes_to_disk

from vkbottle.bot import Blueprint

bp = Blueprint("DatabaseCache")

async def update():
    prev_state = db.cache_state.find_one()
    if prev_state is None:
        prev_state = {"last_checked": 0, "unique_ids": []}
        db.cache_state.insert_one(prev_state)
    
    unique_ids = set(get_unique_ids())
    new_ids = unique_ids - set(prev_state["unique_ids"])
    group_ids = []
    user_ids = []
    for _id in new_ids:
        if _id > 0:
            user_ids.append(_id)
        else:
            group_ids.append(abs(_id))
    new_users = [{
            "name": f"{user.first_name} {user.last_name}",
            "photo_200": user.photo_200,
            "id": user.id
        } for user in await bp.api.users.get(user_ids, fields=['photo_200'])] if len(user_ids) != 0 else [] + \
        await bp.api.groups.get_by_id(group_ids, fields=['photo_200']) if len(group_ids) != 0 else []
    for user in new_users:
        pic_bytes = await download_attachment_by_url(user['photo_200'])
        pic_filepath = save_attachment_bytes_to_disk(pic_bytes)
        db.cache.insert_one({
            'id': user['id'] if 'first_name' in user else -user['id'],
            'name': user['name'],
            'pic': pic_filepath
        })
