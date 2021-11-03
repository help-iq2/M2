import asyncio

from MusicAndVideo.quote import arq
from pytgcalls import idle

from config import call_py


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


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
