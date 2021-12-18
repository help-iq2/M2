import asyncio
import math
import os
import time
import aiofiles
import aiohttp
import wget
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio,    HighQualityVideo,    LowQualityVideo,    MediumQualityVideo
from youtubesearchpython import VideosSearch
from config import HNDLR, bot, call_py
from MusicAndVideo.helpers.queues import QUEUE, add_to_queue, get_queue, clear_queue
from MusicAndVideo.helpers.decorators import authorized_users_only
from MusicAndVideo.helpers.handlers import skip_current_song, skip_item
from __future__ import unicode_literals
from pyrogram.errors import FloodWait, MessageNotModified
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        # CHANGE THIS BASED ON WHAT YOU WANT
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


# video player
def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        # CHANGE THIS BASED ON WHAT YOU WANT
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(filters.command(["تشغيل"], prefixes=f"{HNDLR}"))
async def play(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    m.chat.title
    if replied:
        if replied.audio or replied.voice:
            await m.delete()
            huehue = await replied.reply("**🔄 Memproses**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:35] + "..."
                else:
                    songname = replied.audio.file_name[:35] + "..."
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/d6f92c979ad96b2031cba.png",
                    caption=f"""
**#⃣ Lagu Di Antrian Ke {pos}
🏷️ Judul: [{songname}]({link})
💬 Chat ID: {chat_id}
🎧 Atas Permintaan: {m.from_user.mention}**
""",
                )
            else:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/6213d2673486beca02967.png",
                    caption=f"""
**▶ Mulai Memutar Lagu
🏷️ Judul: [{songname}]({link})
💬 Chat ID: {chat_id}
🎧 Atas Permintaan: {m.from_user.mention}**
""",
                )

    else:
        if len(m.command) < 2:
            await m.reply("Balas ke File Audio atau berikan sesuatu untuk Pencarian")
        else:
            await m.delete()
            huehue = await m.reply("🔎 Pencarian")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await huehue.edit("`Tidak Menemukan Apapun untuk Kueri yang Diberikan`")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**YTDL ERROR ⚠️** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await huehue.delete()
                        # await m.reply_to_message.delete()
                        await m.reply_photo(
                            photo=f"{thumbnail}",
                            caption=f"""
**#⃣ Lagu Di Antrian Ke {pos}
🏷️ Judul: [{songname}]({url})
⏱️ Durasi: {duration}
💬 Chat ID: {chat_id}
🎧 Atas Permintaan: {m.from_user.mention}**
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await huehue.delete()
                            # await m.reply_to_message.delete()
                            await m.reply_photo(
                                photo=f"{thumbnail}",
                                caption=f"""
**▶ Mulai Memutar Lagu
🏷️ Judul: [{songname}]({url})
⏱️ Durasi: {duration}
💬 Chat ID: {chat_id}
🎧 Atas Permintaan: {m.from_user.mention}**
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")


@Client.on_message(filters.command(["تنزيل_فيديو"], prefixes=f"{HNDLR}"))
async def vplay(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    m.chat.title
    if replied:
        if replied.video or replied.document:
            await m.delete()
            huehue = await replied.reply("**🔄 Memproses**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await huehue.edit(
                        "`Hanya 720, 480, 360 Diizinkan` \n`Sekarang Streaming masuk 720p`"
                    )

            if replied.video:
                songname = replied.video.file_name[:35] + "..."
            elif replied.document:
                songname = replied.document.file_name[:35] + "..."

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/d6f92c979ad96b2031cba.png",
                    caption=f"""
**#⃣ Video Di Antrian Ke {pos}
🏷️ Judul: [{songname}]({link})
💬 Chat ID: {chat_id}
🎧 Atas Permintaan: {m.from_user.mention}**
""",
                )
            else:
                if Q == 720:
                    hmmm = HighQualityVideo()
                elif Q == 480:
                    hmmm = MediumQualityVideo()
                elif Q == 360:
                    hmmm = LowQualityVideo()
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(dl, HighQualityAudio(), hmmm),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/6213d2673486beca02967.png",
                    caption=f"""
**▶ Mulai Memutar Video
🏷️ Judul: [{songname}]({link})
💬 Chat ID: {chat_id}
🎧 Atas permintaan: {m.from_user.mention}**
""",
                )

    else:
        if len(m.command) < 2:
            await m.reply(
                "**Balas ke File Audio atau berikan sesuatu untuk Pencarian**"
            )
        else:
            await m.delete()
            huehue = await m.reply("**🔎 Pencarian")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            hmmm = HighQualityVideo()
            if search == 0:
                await huehue.edit(
                    "**Tidak Menemukan Apa pun untuk Kueri yang Diberikan**"
                )
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**YTDL ERROR ⚠️** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await huehue.delete()
                        # await m.reply_to_message.delete()
                        await m.reply_photo(
                            photo=f"{thumbnail}",
                            caption=f"""
**#⃣ Video Di Antrian Ke {pos}
🏷️ Judul: [{songname}]({url})
⏱️ Durasi: {duration}
💬 Chat ID: {chat_id}
🎧 Atas Permintaan: {m.from_user.mention}**
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioVideoPiped(ytlink, HighQualityAudio(), hmmm),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await huehue.delete()
                            # await m.reply_to_message.delete()
                            await m.reply_photo(
                                photo=f"{thumbnail}",
                                caption=f"""
**▶ Mulai Memutar Video
🏷️ Judul: [{songname}]({url})
⏱️ Durasi: {duration}
💬 Chat ID: {chat_id}
🎧 Atas Permintaan: {m.from_user.mention}**
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")


@Client.on_message(filters.command(["اغنيه_عشوائية"], prefixes=f"{HNDLR}"))
async def playfrom(client, m: Message):
    chat_id = m.chat.id
    if len(m.command) < 2:
        await m.reply(            f"**استعمال :** \n\n`{HNDLR}اغنيه عشوائيه  [chat_id/username]` \n`{HNDLR}playfrom [chat_id/username]`"        )
    else:
        args = m.text.split(maxsplit=1)[1]
        if ";" in args:
            chat = args.split(";")[0]
            limit = int(args.split(";")[1])
        else:
            chat = args
            limit = 10
            lmt = 9
        await m.delete()
        hmm = await m.reply(f"🔎 يأخذ {limit} أغنية عشوائية من {chat}**")
        try:
            async for x in bot.search_messages(chat, limit=limit, filter="audio"):
                location = await x.download()
                if x.audio.title:
                    songname = x.audio.title[:30] + "..."
                else:
                    songname = x.audio.file_name[:30] + "..."
                link = x.link
                if chat_id in QUEUE:
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                else:
                    await call_py.join_group_call(
                        chat_id,
                        AudioPiped(location),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                    # await m.reply_to_message.delete()
                    await m.reply_photo(
                        photo="https://telegra.ph/file/6213d2673486beca02967.png",
                        caption=f"""
**▶ ابدأ تشغيل الأغاني من {chat}
🏷️ العنوان : [{songname}]({link})
💬 المحادثه : {chat_id}
🎧 من الطلب : {m.from_user.mention}**
""",
                    )
            await hmm.delete()
            await m.reply(                f"➕ يضيف {lmt} أغنية في قائمة الانتظار \n• ارسل {HNDLR}التشغيل_التلقائي لاضاف اغنيه في القائمه الانتضار**"            )
        except Exception as e:
            await hmm.edit(f"**هناك خطا ** \n`{e}`")


@Client.on_message(filters.command(["التشغيل_التلقائي", "queue"], prefixes=f"{HNDLR}"))
async def playlist(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await m.delete()
            await m.reply(                f"**🎧 تشغيل الان :** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",                disable_web_page_preview=True,            )
        else:
            QUE = f"**🎧 تشغيل الان :** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**⏯ قائمة الانتظار :**"
            l = len(chat_queue)
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                QUE = QUE + "\n" + f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`\n"
            await m.reply(QUE, disable_web_page_preview=True)
    else:
        await m.reply("**❌ لايوجد هناك تشغيل تالي**")
@Client.on_message(filters.command(["التالي"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def skip(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("**❌ لا يوجد شيء في قائمة الانتظار لتخطيه !**")
        elif op == 1:
            await m.reply("قائمة انتظار فارغة ، مغادرة الدردشة الصوتية**")
        else:
            await m.reply(                f"**⏭ تخطي التشغيل ** \n**🎧 التشغيل الان** - [{op[0]}]({op[1]}) | `{op[2]}`",                disable_web_page_preview=True,            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "**🗑️ تمت إزالة الأغاني التالية من قائمة الانتظار : -**"
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


@Client.on_message(filters.command(["انهاء", "ايقاف"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def stop(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("**✅ تم ايقاف التشغيل بنجاح **")
        except Exception as e:
            await m.reply(f"**هناك خطأ ** \n`{e}`")
    else:
        await m.reply("**❌ لايوجد هناك اغنيه شغاله !**")
@Client.on_message(filters.command(["استئناف"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def pause(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(                f"**⏸ تم إيقاف التشغيل مؤقتًا.**\n\n• يمكنك ارجاع التشغيل بواسطه ارسال امر  » `{HNDLR}ايقاف_الاستئناف`"            )
        except Exception as e:
            await m.reply(f"**هناك خطأ ** \n`{e}`")
    else:
        await m.reply("** ❌ لايوجد اغنيه مشتغله !**") 
@Client.on_message(filters.command(["ايقاف_الاستئناف"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def resume(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(                f"**▶ استئناف التشغيل المتوقف مؤقتًا **"            )
        except Exception as e:
            await m.reply(f"**هناك خطأ ** \n`{e}`")
    else:
        await m.reply("**❌ لا شيء متوقف مؤقتا حاليا !**")

@Client.on_message(filters.command(["تحميل", "تنزيل"], prefixes=f"{HNDLR}"))
async def song(client, message: Message):
    urlissed = get_text(message)
    if not urlissed:
        await client.send_message(            message.chat.id,            "صيغة الأمر غير صالحة!",        )
        return
    pablo = await client.send_message(message.chat.id, f"**🔎 Mencari** `{urlissed}`")
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    mio[0]["duration"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    sedlyf = wget.download(kekme)
    opts = {
        "format": "bestaudio",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "720",
            }
        ],
        "outtmpl": "%(id)s.mp3",
        "quiet": True,
        "logtostderr": False,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(mo, download=True)
    except Exception as e:
        await pablo.edit(f"**Failed To Download** \n**Error :** `{str(e)}`")
        return
    c_time = time.time()
    capy = f"""
**🏷️ اسم الاغنيه :** [{thum}]({mo})
**🎧 طلب من :** {message.from_user.mention}
"""
    file_stark = f"{ytdl_data['id']}.mp3"
    await client.send_audio(        message.chat.id,        audio=open(file_stark, "rb"),        duration=int(ytdl_data["duration"]),        title=str(ytdl_data["title"]),        performer=str(ytdl_data["uploader"]),        thumb=sedlyf,        caption=capy,        progress=progress,        progress_args=(            pablo,            c_time,            f"**📥 تحميل** `{urlissed}`",            file_stark,        ),    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)


def get_text(message: Message) -> [None, str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None


def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


async def progress(current, total, message, start, type_of_ps, file_name=None):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        if elapsed_time == 0:
            return
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "{0}{1} {2}%\n".format(            "".join("🔴" for i in range(math.floor(percentage / 10))),            "".join("🔘" for i in range(10 - math.floor(percentage / 10))),            round(percentage, 2),        )

        tmp = progress_str + "{0} of {1}\nETA: {2}".format(            humanbytes(current), humanbytes(total), time_formatter(estimated_total_time)        )
        if file_name:
            try:
                await message.edit(                    "{}\n**اسم الفايل:** `{}`\n{}".format(type_of_ps, file_name, tmp)                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass
        else:
            try:
                await message.edit("{}\n{}".format(type_of_ps, tmp))
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass


def get_user(message: Message, text: str) -> [int, str, None]:
    asplit = None if text is None else text.split(" ", 1)
    user_s = None
    reason_ = None
    if message.reply_to_message:
        user_s = message.reply_to_message.from_user.id
        reason_ = text or None
    elif asplit is None:
        return None, None
    elif len(asplit[0]) > 0:
        user_s = int(asplit[0]) if asplit[0].isdigit() else asplit[0]
        if len(asplit) == 2:
            reason_ = asplit[1]
    return user_s, reason_


def get_readable_time(seconds: int) -> int:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time


def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " يوم(s), ") if days else "")
        + ((str(hours) + " ساعه(s), ") if hours else "")
        + ((str(minutes) + " دقائق(s), ") if minutes else "")
        + ((str(seconds) + " ثواني(s), ") if seconds else "")
        + ((str(milliseconds) + " ميل ثانيه(s), ") if milliseconds else "")
    )
    return tmp[:-2]


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


# Funtion To Download Song
async def download_song(url):
    song_name = f"{randint(6969, 6999)}.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(song_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return song_name


is_downloading = False


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


@Client.on_message(filters.command(["تنزيل_فيديو", "تحميل_فيديو"], prefixes=f"{HNDLR}"))
async def vsong(client, message: Message):
    urlissed = get_text(message)

    pablo = await client.send_message(message.chat.id, f"**🔎 يبحث عن** `{urlissed}`")
    if not urlissed:
        await pablo.edit(            "صيغة الأمر غير صالحة!"        )
        return

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        await event.edit(event, f"**التحميل فشل** \n `{str(e)}`")
        return
    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"""
**🏷️ اسم الفيديو :** [{thum}]({mo})
**🎧 طلب من :** {message.from_user.mention}
"""
    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        progress=progress,
        progress_args=(
            pablo,
            c_time,
            f"**📥 تحميل** `{urlissed}`",
            file_stark,
        ),
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
