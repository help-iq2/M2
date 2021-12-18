from pyrogram.raw.base import Update
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio,    HighQualityVideo,    LowQualityVideo,    MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded, StreamVideoEnded
from config import call_py
from MusicTelethon.helpers.queues import QUEUE, clear_queue, get_queue, pop_an_item

async def skip_current_song(chat_id):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            return 1
        else:
            songname = chat_queue[1][0]
            url = chat_queue[1][1]
            link = chat_queue[1][2]
            type = chat_queue[1][3]
            Q = chat_queue[1][4]
            if type == "Audio":
                await call_py.change_stream(                    chat_id,                    AudioPiped(                        url,                    ),                )
            elif type == "Video":
                if Q == 720:
                    hm = HighQualityVideo()
                elif Q == 480:
                    hm = MediumQualityVideo()
                elif Q == 360:
                    hm = LowQualityVideo()
                await call_py.change_stream(                    chat_id, AudioVideoPiped(url, HighQualityAudio(), hm)                )
            pop_an_item(chat_id)
            return [songname, link, type]
    else:
        return 0
async def skip_item(chat_id, h):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        try:
            x = int(h)
            songname = chat_queue[x][0]
            chat_queue.pop(x)
            return songname
        except Exception as e:
            print(e)
            return 0
    else:
        return 0
@call_py.on_stream_end()
async def on_end_handler(_, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        print(chat_id)
        await skip_current_song(chat_id)
@call_py.on_stream_end()
async def on_end_handler(_, update: Update):
    if isinstance(update, StreamVideoEnded):
        chat_id = update.chat_id
        print(chat_id)
        await skip_current_song(chat_id)
@call_py.on_closed_voice_chat()
async def close_handler(client: PyTgCalls, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
