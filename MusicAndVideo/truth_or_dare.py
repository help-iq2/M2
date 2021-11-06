import requests
from pyrogram import Client

from MusicAndVideoPlayer.helpers.filters import command


@Client.on_message(command(["truth", "kejujuran"]))
async def truth(client, message):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/truth").json()
        results = f"{resp['message']}"
        return await message.reply_text(results)
    except Exception:
        await message.reply_text("Lagi error truth nya")

@Client.on_message(command(["dare", "tantangan"]))
async def dare(client, message):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/dare").json()
        results = f"{resp['message']}"
        return await message.reply_text(results)
    except Exception:
        await message.reply_text("Lagi error dare nya")
