from typing import Callable
from pyrogram import Client
from pyrogram.types import Message
from config import SUDO_USERS
from MusicTelethon.helpers.admins import get_administrators
def authorized_users_only(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        if message.from_user.id in SUDO_USERS:
            return await func(client, message)

        administrators = await get_administrators(message.chat)

        for administrator in administrators:
            if administrator == message.from_user.id:
                return await func(client, message)

    return decorator
