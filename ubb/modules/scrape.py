import re
import asyncio
import os
import io
import time
import logging

from telethon import events, types, errors
from telethon.tl.functions.messages import GetHistoryRequest
from ..func import http
from bs4 import BeautifulSoup as bs
from ubb import Ubot, DUMP_ID
from datetime import datetime


d = datetime.now()
m = d.strftime("%m")
y = d.strftime("%Y")


@Ubot.on(events.NewMessage(pattern=r'\.scrape'))
async def scrapper(event):
    # use .scrape [channel_id or username] 100
    # default limit 100 u can scrape below 100 at a time
    target, limit = event.message.message[len('.scrape '):].split()
    if str(target).startswith('-1'):
        target = int(target)
    posts = await Ubot(
        GetHistoryRequest(
            peer=target, 
            limit=int(limit), 
            offset_date=None, 
            offset_id=0, 
            max_id=0, 
            min_id=0,
            add_offset=0,
            hash=0)
    )
    cards = re.findall(r"message='([^']+)", posts.stringify())
    RAWCC = []
    for cc in cards:
        try:
            x = re.findall('[0-9]+', cc)
            cn = x[0]
            mm = x[1]
            yy = x[2]
            cvv = x[3]
            if str(mm).startswith('2'):
                mm, yy = yy, mm
            if len(mm) >= 3: 
                mm, yy, cvv = yy, cvv, mm
            if len(mm) == 1:
                mm = f'0{mm}'
            if len(yy) == 2:
                yy = f'20{yy}'
            if mm+yy <= m+y:
                continue
            value = f'{cn}|{mm}|{yy}|{cvv}\n'
            regex = re.compile(r'((?:(^(4|5|6)[0-9]{15,15})|(^3[0-9]{14,14}))\|[0-9]{1,2}\|[0-9]{2,4}\|[0-9]{3,4})')
            if regex.match(value):
                RAWCC.append(value)  # append valid format ccs!
        except:
            pass
        
    CLEAN = set(RAWCC) # rm duplicates from list
    for CC in CLEAN:
        with io.open(f'{target}.txt', 'a') as f:
            f.write(CC)
    await Ubot.send_file(event.peer_id,
                         f'{target}.txt', 
                         caption=f'**CC Scrapper\nNo. of cards from {target}: {len(CLEAN)}\nUserBotBy-» @Xbinner2**',
                         force_document=True)
    os.remove(f'{target}.txt') # rm old file to prevent duplicates
    
    






# Enable logging
logging.basicConfig(level=logging.INFO)

# Create a queue to store messages
message_queue = asyncio.Queue()

@Ubot.on(events.NewMessage())
async def check_incoming_messages(event):
    

    me = await Ubot.get_me()
    if event.sender_id == me.id:
        return

    entities = event.message.entities
    prefixes = ['?', '/', '.', '!']
    m = event.message.message

    if m.startswith(tuple(prefixes)) or len(m) < 25 or event.is_private or len(m) > 600:
        return

    is_cc = False
    if entities:
        for entity in entities:
            if isinstance(entity, types.MessageEntityBankCard):
                is_cc = True
            if is_cc:
                try:
                    x = re.findall(r'\d+', m)
                    if len(x) > 10:
                        return
                    BIN = re.search(r'\d{15,16}', m)[0][:6]

                    # Add the message and event to the queue
                    await message_queue.put((event.message.id, m, event))

                except errors.FloodWaitError as e:
                    logging.error(f'Flood wait: {e.seconds}')
                    await asyncio.sleep(e.seconds)

# Create a function to forward messages from the queue
async def forward_messages():
    while True:
        try:
            message_id, message_content, event = await message_queue.get()

            # Check if the original message still exists
            try:
                original_message = await Ubot.get_messages(event.input_chat, ids=[message_id])
            except errors.MessageIdInvalidError:
                logging.info("Original message was deleted before forwarding.")
                continue

            # Wait for a certain time (e.g., 3 seconds) before forwarding
            await asyncio.sleep(1)

            # Forward the message
            await Ubot.send_message(DUMP_ID, message_content)

            # Remove the message from the queue
            message_queue.task_done()

        except Exception as e:
            logging.error(f"Error while forwarding message: {str(e)}")

# Run the event loop provided by telethon
with Ubot:
    Ubot.loop.run_until_complete(forward_messages())


