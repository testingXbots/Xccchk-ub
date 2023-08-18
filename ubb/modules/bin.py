import re
import asyncio
from telethon import events
from ubb import Ubot
from ubb.func import http

@Ubot.on(events.NewMessage(pattern=r'\.bin'))
async def srbin(event):
    BIN = event.message.message[len('.bin '):]
    reply_msg = await event.get_reply_message()
    if reply_msg:
        BIN = reply_msg.message
    try:
        _BIN = re.sub(r'[^0-9]', '', BIN)
        _res = await http.get(f'http://binchk-api.vercel.app/bin={_BIN}')
        res = _res.json()

        # Post the message and get the message object
        msg = await event.reply('Processing...')

        # Wait for a very short duration before checking if the message still exists
        await asyncio.sleep(2)  # Adjust this value as needed

        # Check if the message still exists in the channel
        try:
            await event.client.get_messages(event.input_chat, ids=[msg.id])
        except:
            return  # Message was deleted, so no further action needed

        new_msg = f'''
BIN: `{_BIN}`
Brand⇢ **{res["brand"]}**
Type⇢ **{res["type"]}**
Level⇢ **{res["level"]}**
Bank⇢ **{res["bank"]}**
Phone⇢ **{res["phone"]}**
Flag⇢ **{res["flag"]}**
Currency⇢ **{res["currency"]}**
Country⇢ **{res["country"]}({res["code"]})**
'''

        # Edit the message with the new content
        await msg.edit(new_msg)
    except:
        await msg.edit('Failed to parse bin data from api')
