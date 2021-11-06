from typing import List, Union

from pyrogram import filters

from config import COMMAND_PREFIXES, SUDO_USERS

other_filters = filters.group & ~filters.edited & ~filters.via_bot & ~filters.forwarded
other_filters2 = (
    filters.private & ~filters.edited & ~filters.via_bot & ~filters.forwarded
)
sudo_only = filters.user(SUDO_USERS)


def command(commands: Union[str, List[str]]):
    return filters.command(commands, COMMAND_PREFIXES)
