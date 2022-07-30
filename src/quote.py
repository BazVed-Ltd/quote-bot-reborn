from hashlib import blake2s
from typing import Tuple
from vkbottle.bot import Message
from vkbottle_types.objects import (
    MessagesMessageAttachment as MessageAttachment,
    MessagesMessageAttachmentType as MessageAttachmentType,
    PhotosPhoto as Photo,
    PhotosPhotoSizes as PhotoSizes,
    BaseSticker as Sticker,
)
import io
import os
import aiohttp
from PIL import Image
from hashlib import blake2s


# TODO: Нужно будет это либо в конфиг, либо ещё что-то придумать
ATTACHMENTS_DIR = "./priv"
QUOTES_VERSION = 1


class Quote:
    """Представляет цитату

    Также см. `Phrase`
    - `Quote.from_message()` создаёт экземпляр класса из `vkbottle.bot.Message`
    - `Quote.clean_fields()` возвращает используемые поля
    """

    required_fields = "date peer_id from_id fwd_messages version".split()

    id: int = None
    date: int
    peer_id: int
    from_id: int
    fwd_messages: list["Phrase"]
    version: int = QUOTES_VERSION

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        for field in self.required_fields:
            if not hasattr(self, field):
                raise ValueError(f"args must have {field} field")

    def clean_fields(self) -> dict:
        """Возвращает используемые поля

        Для вложенных структур вызывает их методы `clean_fields()`, прим. см. `Quote.clean_fwd_messages_fields()`.
        """
        return {
            "id": self.id,
            "date": self.date,
            "peer_id": self.peer_id,
            "from_id": self.from_id,
            "fwd_messages": self.clean_fwd_messages_fields(),
            "version": self.version,
        }

    def clean_fwd_messages_fields(self) -> dict:
        """Вызывает метод clean_fields() для объектов в списке `Quote.fwd_messages`"""
        return [msg.clean_fields() for msg in self.fwd_messages]

    @classmethod
    async def from_message(cls, message: Message, **kwargs) -> "Quote":
        """Создаёт цитату из `vkbottle.bot.Message`

        Коллизия `message.id` с `Quote.id`, потому `message.id` удаляется. Для элементов `fwd_messages` вызывается
        `Phrase.from_message()`. Ради однородности `message.reply_message` сохраняется в список `fwd_messages`.
        Приоритет полей такой: `fwd_messages` > `kwargs` > `message`. Поэтому заданный в `kwargs.fwd_messages` проигнорируется. 
        """
        del message.id  # TODO: Т.н. "неуклюжий" код, но ничего другого не придумал.

        if message.fwd_messages:
            fwd_messages = [await Phrase.from_message(msg) for msg in message.fwd_messages]
        elif message.reply_message:
            fwd_messages = [await Phrase.from_message(message.reply_message)]
        else:
            fwd_messages = []

        # Приоритет: fwd_messages > kwargs > message
        all_fields = message.__dict__
        all_fields.update(kwargs)
        all_fields.update(fwd_messages=fwd_messages)

        return cls(**all_fields)

    @classmethod
    def from_dict(cls, fields) -> "Quote":
        """Аналог `from_message`, но для словарей

        Используется для загрузки из базы данных.
        """
        fields["fwd_messages"] = [Phrase.from_dict(
            msg) for msg in fields["fwd_messages"]]
        return cls(**fields)


class Phrase(Quote):
    """То же самое, что и `Quote`, но с другими полями

    См. `Quote`
    """
    required_fields = "from_id date text fwd_messages attachments".split()

    from_id: int
    date: int
    text: str
    fwd_messages: list()
    attachments: list()

    def clean_fields(self) -> dict:
        """Возвращает используемые поля

        Копирует поведение `Quote.clean_fields()`.
        """
        return {
            "from_id": self.from_id,
            "date": self.date,
            "text": self.text,
            "fwd_messages": self.clean_fwd_messages_fields(),
            "attachments": [att.clean_fields() for att in self.attachments],
        }

    @classmethod
    async def from_message(cls, message: Message) -> "Attachment":
        """Создаёт цитату из `vkbottle.bot.Message`

        Загружает вложения и затем вызывает `Quote.from_message`.
        """
        attachments = []
        for attachment in message.attachments:
            try:
                attachments.append(await Attachment.download(attachment))
            except TypeError:
                pass
        return await super().from_message(message, attachments=attachments)

    @classmethod
    def from_dict(cls, fields) -> "Quote":
        """Аналог `from_message`, но для словарей

        Обрабатывает вложения и вызывает `Quote.from_dict()`.
        """
        fields["attachments"] = [Attachment.from_dict(
            att) for att in fields["attachments"]]
        return super().from_dict(fields)


class Attachment(dict):
    """Вложения в сообщениях

    - `Attachment.clean_fields()` - возвращает используемые поля
    - `Attachment.download()` - главная функция, загружает и сохраняет вложение

    Поле `filepath`, в зависимости от `downloaded` может хранить либо ссылку на сервер ВК,
    либо путь к локальному файлу.
    """
    required_fields = "type filepath downloaded".split()

    type: str
    filepath: str
    downloaded: bool

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(**kwargs)

        for field in self.required_fields:
            if not hasattr(self, field):
                raise ValueError(f"args must have {field} field")

    def clean_fields(self) -> dict:
        """Возвращает используемые поля"""
        return {
            "type": self.type,
            "fielpath": self.filepath,
        }

    @classmethod
    async def download(cls, attachment: MessageAttachment) -> "Attachment":
        """Сохраняет ссылки на вложения, при необходимости скачивает вложения"""
        downloaded=False

        match attachment.type:  # TODO: добавить другие типы
            case MessageAttachmentType.PHOTO: 
                filepath = await download_photo(attachment.photo)
                downloaded = True
            case MessageAttachmentType.STICKER:
                filepath = get_max_size_photo(attachment.sticker.images).url
            case _:
                raise TypeError("unsupported attachment type")

        all_fields = attachment.__dict__
        # Enum не подходит, переводим в строку
        all_fields.update(type=attachment.type.name.lower())
        return cls(filepath=filepath, downloaded=downloaded, **all_fields)

    @classmethod
    def from_dict(cls, fields: dict) -> "Attachment":
        """Аналог `download`, но подразумевает уже существующий в директории файл"""
        return cls(**fields)


async def download_photo(photo: Photo) -> str:
    photo_url = get_max_size_photo(photo.sizes).url
    photo_bytes = await download_attachment_by_url(photo_url)
    photo_hash = calculate_hash(photo_bytes)
    _, filepath = photo_paths(photo_hash)
    save_file_if_not_exist(filepath, photo_bytes)
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
