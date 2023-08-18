import re
import asyncio
from telethon import events
from ubb import Ubot
from ubb.func import http

@Ubot.on(events.NewMessage(pattern=r'\.bin'))
async def srbin(event):
    await asyncio.sleep(6)
    BIN = event.message.message[len('.bin '):]
    reply_msg = await event.get_reply_message()
    if reply_msg:
        BIN = reply_msg.message
    try:
        _BIN = re.sub(r'[^0-9]', '', BIN)
        _res = await http.get(f'http://binchk-api.vercel.app/bin={_BIN}')
        res = _res.json()
        
        # Get the message's unique ID
        msg_id = event.message.id
        
        # Retrieve the message using its ID
        messages = await event.client.get_messages(event.input_chat, ids=[msg_id])
        
        # If the message doesn't exist anymore, return without processing
        if not messages:
            return
        
        msg = f'''
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
        
        # Wait for 4 seconds before editing the message
        await asyncio.sleep(4)
        
        await event.edit(msg)
    except:
        await event.edit('Failed to parse bin data from api')
