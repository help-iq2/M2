import io
import os
import random

from PIL import Image
from pyrogram import Client, emoji, filters
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName
from pyrogram.types import Message

from config import DOWN_PATH, HNDLR, call_py


@Client.on_message(filters.command(["kang"], prefixes=f"{HNDLR}"))
async def kang_(client, message: Message):
    """kang a sticker"""
    user = await call_py.get_me()
    replied = message.reply_to_message
    photo = None
    _emoji = None
    emoji_ = ""
    is_anim = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif replied.sticker:
            if not replied.sticker.file_name:
                await message.reply("`Stiker tidak memiliki Nama!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            if not replied.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            await message.edit("`File Tidak Didukung!`")
            return
        await message.edit("`wih bagus colong ah`")
        photo = await call_py.download_media(message=replied, file_name=DOWN_PATH)
    else:
        await message.edit("`Saya tidak bisa mengerti itu...`")
        return
    if photo:
        args = message.filtered_input_str.split(" ")
        pack = 1
        if len(args) == 2:
            _emoji, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                _emoji = args[0]

        if _emoji is not None:
            _saved = emoji_
            for k in _emoji:
                if k and k in (
                    getattr(emoji, a) for a in dir(emoji) if not a.startswith("_")
                ):
                    emoji_ += k
            if _saved and _saved != emoji_:
                emoji_ = emoji_[len(_saved) :]
        if not emoji_:
            emoji_ = "✨"

        u_name = user.username
        if u_name:
            u_name = "@" + u_name
        else:
            u_name = user.first_name or user.id
        packname = f"{user.id} {pack}"
        custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}"
        packnick = f"{custom_packnick} {pack}"
        cmd = "/newpack"
        if resize:
            photo = resize_photo(photo)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        exist = False
        try:
            exist = await message.client.send(
                GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname))
            )
        except StickersetInvalid:
            pass
        if exist is not False:
            async with client.conversation("Stickers", limit=120) as conv:
                try:
                    await conv.send_message("/addsticker")
                except YouBlockedUser:
                    await message.edit("pertama **buka blokir** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                limit = "50" if is_anim else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"{user.id} {pack}"
                    packnick = f"{custom_packnick} {pack}"
                    if is_anim:
                        packname += "_anim"
                        packnick += " (Animated)"
                    await message.edit(
                        "`Beralih ke Paket "
                        + str(pack)
                        + " karena ruang yang tidak mencukupi`"
                    )
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Paket yang dipilih tidak valid.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(photo)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(emoji_)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response(mark_read=True)
                            await conv.send_message(f"<{packnick}>", parse_mode=None)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/skip")
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packname)
                        await conv.get_response(mark_read=True)
                        if "-d" in message.flags:
                            await message.delete()
                        else:
                            out = (
                                "__kanged__"
                                if "-s" in message.flags
                                else f"[kanged](t.me/addstickers/{packname})"
                            )
                            await message.edit(
                                f"**Sticker** {out} __dalam Paket Berbeda__**!**"
                            )
                        return
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Maaf, jenis file tidak valid." in rsp.text:
                    await message.edit(
                        "`Gagal menambahkan stiker, gunakan` @Stickers "
                        "`bot untuk menambahkan stiker secara manual.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/done")
                await conv.get_response(mark_read=True)
        else:
            await message.edit("`Membuat Paket baru...`")
            async with client.conversation("Stickers") as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await message.edit("first **buka blokir** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Maaf, jenis file tidak valid." in rsp.text:
                    await message.edit(
                        "`Gagal menambahkan stiker, gunakan` @Stickers "
                        "`bot untuk menambahkan stiker secara manual.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response(mark_read=True)
                    await conv.send_message(f"<{packnick}>", parse_mode=None)
                await conv.get_response(mark_read=True)
                await conv.send_message("/skip")
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                await conv.get_response(mark_read=True)
        if "-d" in message.flags:
            await message.delete()
        else:
            out = (
                "__kanged__"
                if "-s" in message.flags
                else f"[kanged](t.me/addstickers/{packname})"
            )
            await message.edit(f"**Sticker** {out}**!**")
        if os.path.exists(str(photo)):
            os.remove(photo)


def resize_photo(photo: str) -> io.BytesIO:
    """Resize the given photo to 512x512"""
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(photo)
    return resized_photo


KANGING_STR = (
    "Menggunakan Ilmu Sihir untuk memasang stiker ini...",
    "Menjiplak hehe...",
    "Mengundang stiker ini ke paket saya...",
    "Kinging stiker ini...",
    "Hei itu stiker yang bagus!\nKeberatan kalau aku kang?!..",
    "hehe saya stel ur stikér\nhehe.",
    "Ay lihat ke sana (☉｡☉)!→\nSementara aku kang ini...",
    "Mawar itu merah violet itu biru, kanging stiker ini jadi pacc saya terlihat keren",
    "Memenjarakan stiker ini...",
    "Mr.Steal Stiker Anda mencuri stiker ini ... ",
)

TEXTILE = random.choice(KANGING_STR)
