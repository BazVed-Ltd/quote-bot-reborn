from vkbottle.bot import Message, Blueprint
from vkbottle_types.objects import (
    MessagesMessageAttachment as MessageAttachment,
    MessagesMessageAttachmentType as MessageAttachmentType,
    PhotosPhoto as Photo,
    PhotosPhotoSizes as PhotoSizes,
    DocsDoc as Doc,
    MessagesGraffiti as Graffiti,
)
import io
import os
import aiohttp
from PIL import Image
from hashlib import blake2s
from typing import Tuple

from quote_bot.rules import NameArguments, CommandRule
from quote_bot.database import quotes as quotes_db

bp = Blueprint("Quotes")

ATTACHMENTS_DIR = "attachments"
QUOTES_VERSION = 1


@bp.on.message(NameArguments("deep", "d"), CommandRule("сьлржалсч", ["/"], -1))
async def save_quote_handler(message: Message, deep: str, d: str):
    try:
        quote_deep = int(deep or d or -1)
        if not (quote_deep >= 0 or quote_deep == -1):
            raise ValueError
    except ValueError:
        return "Глубинность должна быть ЧИСЛОМ >= 0 или -1"
    
    if not message.fwd_messages and not message.reply_message:
        return "И че сохранить-то надо"

    quote = await message_to_dict(message, deep=quote_deep)

    quote = quotes_db.insert_quote(quote)

    return str(quote["id"])  # TODO: Нужно возвращать ссылку на сайт с цитатой

# TODO: Реализовать как в оригинале. На данный момент нужен для разработки


@bp.on.message(NameArguments("j"), CommandRule("сь", ["/"], -1))
async def save_quote_handler(message: Message, j=None):
    if j:
        return str(quotes_db.get_quote_by_id(int(j)))
    return "Ещё не готово, используй -j"


async def message_to_dict(message: Message, deep: int = -1) -> dict:
    result = {}
    result["date"] = message.date
    result["peer_id"] = message.peer_id
    result["from_id"] = message.from_id
    result["version"] = QUOTES_VERSION

    from_reply = bool(message.reply_message)

    result["fwd_messages"] = [await fwd_message_to_dict(msg, from_reply=from_reply, deep=deep) for msg in get_fwd_messages(message)]
    return result


async def fwd_message_to_dict(message: Message, from_reply=False, deep: int = -1) -> dict:
    if from_reply:
        messages = await bp.api.messages.get_by_id(message_ids=[message.id])
        message = messages.items[0]
    result = {}
    result["from_id"] = message.from_id
    result["date"] = message.date
    result["text"] = message.text

    inner_from_reply = bool(message.reply_message)

    if deep != 0:
        result["fwd_messages"] = [await fwd_message_to_dict(msg, from_reply=inner_from_reply, deep=deep-1) for msg in get_fwd_messages(message)]
    else:
        result["fwd_messages"] = []

    result["attachments"] = [await attachment_to_dict(attachment) for attachment in message.attachments]
    return result


def get_fwd_messages(message: Message) -> list[Message]:
    if message.fwd_messages:
        return message.fwd_messages
    elif message.reply_message:
        return [message.reply_message]
    else:
        return []


async def attachment_to_dict(attachment: MessageAttachment) -> dict:
    result = {"downloaded": False}

    a_type = attachment.type
    if a_type == MessageAttachmentType.PHOTO:
        result["filepath"] = await save_photo(attachment.photo)
        result["downloaded"] = True
    elif a_type == MessageAttachmentType.DOC:
        result["filepath"] = await save_doc(attachment.doc)
        result["downloaded"] = True
    elif a_type == MessageAttachmentType.GRAFFITI:
        result["filepath"] = await save_graffiti(attachment.graffiti)
    elif a_type == MessageAttachmentType.STICKER:
        result["filepath"] = get_max_size_photo(attachment.sticker.images).url
    elif a_type == MessageAttachmentType.AUDIO_MESSAGE:
        result["filepath"] = attachment.audio_message.link_mp3
    else:
        raise TypeError("unsupported attachment type")

    return result


async def save_photo(photo: Photo) -> str:
    photo_url = get_max_size_photo(photo.sizes).url
    photo_bytes = await download_attachment_by_url(photo_url)
    return save_attachment_bytes_to_disk(photo_bytes)


async def save_doc(doc: Doc) -> str:
    # FIXME: Тут, очевидно, правильно сохраняются только гифки и изображения
    doc_bytes = await download_attachment_by_url(doc.url)
    return save_attachment_bytes_to_disk(doc_bytes)


async def save_graffiti(graffiti: Graffiti) -> str:
    graffiti_bytes = await download_attachment_by_url(graffiti.url)
    return save_attachment_bytes_to_disk(graffiti_bytes)


def save_attachment_bytes_to_disk(att_bytes: bytes) -> str:
    att_hash = calculate_hash(att_bytes)
    _, filepath = photo_paths(att_hash)
    save_file_if_not_exist(filepath, att_bytes)
    return filepath


def get_max_size_photo(sizes: list[PhotoSizes]) -> PhotoSizes:
    return max(sizes, key=lambda size: size.height * size.width)


def photo_paths(photo_hash: str) -> Tuple[str, str]:
    filename = f"{photo_hash}.webp"
    filepath = os.path.join(ATTACHMENTS_DIR, filename)
    return filename, filepath


def calculate_hash(data: bytes) -> str:
    return blake2s(data).hexdigest()


async def download_attachment_by_url(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            img = await resp.read()
    return img


def save_file_if_not_exist(filepath: str, data: bytes) -> None:
    if not os.path.exists(filepath):
        with Image.open(io.BytesIO(data)) as images:
            images.save(filepath, 'WEBP', save_all=True)
