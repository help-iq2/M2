import datetime

from pyrogram.errors import MessageDeleteForbidden
from pyrogram import Client, filters
from pyrogram.types import Message

from config import HNDLR


@Client.on_message(filters.command(["purge", "hapus"], prefixes=f"{HNDLR}"))
async def purge_(message: Message):
    """purge from replied message"""
    await message.edit("`purging ...`")
    from_user_id = None
    if message.filtered_input_str:
        from_user_id = (await message.client.get_users(message.filtered_input_str)).id
    start_message = 0
    if "l" in message.flags:
        limit = int(message.flags["l"])
        limit = min(limit, 100)
        start_message = message.message_id - limit
    if message.reply_to_message:
        start_message = message.reply_to_message.message_id
        if "u" in message.flags:
            from_user_id = message.reply_to_message.from_user.id
    if not start_message:
        await message.err("invalid start message!")
        return
    list_of_messages = []
    purged_messages_count = 0

    async def handle_msg(a_message):
        nonlocal list_of_messages, purged_messages_count
        if (
            from_user_id
            and a_message
            and a_message.from_user
            and a_message.from_user.id == from_user_id
        ):
            list_of_messages.append(a_message.message_id)
        if not from_user_id:
            list_of_messages.append(a_message.message_id)
        if len(list_of_messages) >= 100:
            try:
                await message.client.delete_messages(
                    chat_id=message.chat.id, message_ids=list_of_messages
                )
            except MessageDeleteForbidden:
                return
            purged_messages_count += len(list_of_messages)
            list_of_messages = []

    start_t = datetime.datetime.now()
    if message.client.is_bot:
        for a_message in await message.client.get_messages(
            chat_id=message.chat.id,
            replies=0,
            message_ids=range(start_message, message.message_id),
        ):
            await handle_msg(a_message)
    else:
        async for a_message in message.client.iter_history(
            chat_id=message.chat.id, limit=None, offset_id=start_message, reverse=True
        ):
            await handle_msg(a_message)
    if list_of_messages:
        try:
            await message.client.delete_messages(
                chat_id=message.chat.id, message_ids=list_of_messages
            )
        except MessageDeleteForbidden:
            return
        purged_messages_count += len(list_of_messages)
    end_t = datetime.datetime.now()
    time_taken_s = (end_t - start_t).seconds
    out = f"<u>purged</u> {purged_messages_count} messages in {time_taken_s} seconds."
    await message.edit(out, del_in=3)


@Client.on_message(filters.command(["purgeme", "hapussaya"], prefixes=f"{HNDLR}"))
async def purgeme_(message: Message):
    """purge given no. of your messages"""
    await message.edit("`purging ...`")
    if not (message.input_str and message.input_str.isdigit()):
        return await message.err(
            "Provide a valid number of message to delete", del_in=3
        )
    start_t = datetime.datetime.now()
    number = min(int(message.input_str), 100)
    mid = message.message_id
    msg_list = []
    # https://t.me/pyrogramchat/266224
    # search_messages takes some minutes to index new messages
    # so using iter_history to get messages newer than 5 mins.
    old_msg = (start_t - datetime.timedelta(minutes=5)).timestamp()

    async for msg in userge.search_messages(
        message.chat.id, "", limit=number, from_user="me"
    ):
        msg_list.append(msg.message_id)

    async for new_msg in userge.iter_history(message.chat.id, offset_id=mid, offset=0):
        if new_msg.from_user.is_self:
            msg_list.append(new_msg.message_id)
        if old_msg > new_msg.date or (msg_list and (msg_list[-1] > new_msg.message_id)):
            break

    # https://stackoverflow.com/questions/39734485/python-combining-two-lists-and-removing-duplicates-in-a-functional-programming
    del_list = list(set(msg_list))
    if mid in del_list:
        del_list.remove(mid)
    del_list.reverse()
    del_list_ = del_list[:number]

    await userge.delete_messages(message.chat.id, message_ids=del_list_)

    end_t = datetime.datetime.now()
    time_taken_s = (end_t - start_t).seconds
    out = f"<u>purged</u> {len(del_list_)} messages in {time_taken_s} seconds."
    await message.edit(out, del_in=3)
