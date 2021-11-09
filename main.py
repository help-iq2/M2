import asyncio

from pytgcalls import idle

from config import call_py
from MusicAndVideo.quote import arq


async def main():
    await call_py.start()
    print(
        """
    ------------------
   | Userbot Started! |
    ------------------
"""
    )
    await idle()
    await arq.close()
