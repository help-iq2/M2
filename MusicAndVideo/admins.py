from pyrogram import Client, filters
from pyrogram.types import Message

from config import HNDLR, call_py
from MusicAndVideo.helpers.decorators import authorized_users_only
from MusicAndVideo.helpers.handlers import skip_current_song, skip_item
from MusicAndVideo.helpers.queues import QUEUE, clear_queue
from MusicAndVideoPlayer.helpers.filters import command, other_filters


@Client.on_message(command(["skip", "lewat"]) & other_filters)
@authorized_users_only
async def skip(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("**❌ Tidak ada apapun didalam antrian untuk dilewati!**")
        elif op == 1:
            await m.reply("Antrian Kosong, Meninggalkan Obrolan Suara**")
        else:
            await m.reply(
                f"**⏭ Melewati pemutaran** \n**🎧 Sekarang memutar** - [{op[0]}]({op[1]}) | `{op[2]}`",
                disable_web_page_preview=True,
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "**🗑️ Menghapus lagu-lagu berikut dari Antrian: -**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#⃣{x}** - {hm}"
            await m.reply(OP)


@Client.on_message(command(["end", "stop"]) & other_filters)
@authorized_users_only
async def stop(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("**✅ Mengakhiri pemutaran**")
        except Exception as e:
            await m.reply(f"**ERROR** \n`{e}`")
    else:
        await m.reply("**❌ Tidak ada apapun yang sedang diputar!**")


@Client.on_message(command(["pause", "jeda"]) & other_filters)
@authorized_users_only
async def pause(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(
                f"**⏸ Pemutaran dijeda.**\n\n• Untuk melanjutkan pemutaran, gunakan perintah » {HNDLR}resume"
            )
        except Exception as e:
            await m.reply(f"**ERROR** \n`{e}`")
    else:
        await m.reply("** ❌ Tidak ada apapun yang sedang diputar!**")


@Client.on_message(command(["resume", "lanjut"]) & other_filters)
@authorized_users_only
async def resume(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(
                f"**▶ Melanjutkan pemutaran yang dijeda**\n\n• Untuk menjeda pemutaran, gunakan perintah » {HNDLR}pause**"
            )
        except Exception as e:
            await m.reply(f"**ERROR** \n`{e}`")
    else:
        await m.reply("**❌ Tidak ada apapun yang sedang dijeda!**")
