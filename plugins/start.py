# Don't Remove Credit Tg - @RS_WONER
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@RS_WONER
# Ask Doubt on telegram @RS_WONER

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db

# HELP_TXT directly here to avoid import issues
HELP_TXT = """**🌟 Help Menu - RS Save Restricted Bot** 

**How to use this bot:**

**For Public Channels:**
```
https://t.me/channelname/message_id
```
**For Private Channels:**
```
https://t.me/c/channel_id/message_id

```
**For Bot Chats:**
```
https://t.me/b/botusername/message_id

```
**Multiple Posts (Range):**
```
https://t.me/channelname/1001-1010
https://t.me/c/channelid/101-120

```
**Steps:**
1. First use `/login` to login with your account
2. Send the post link to download restricted content
3. Use `/cancel` to stop any ongoing process

**Note:** The bot will download content that your logged-in account has access to."""

class batch_temp(object):
    IS_BATCH = {}

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    buttons = [
        [
            InlineKeyboardButton("❣️ Developer", url="https://t.me/RS_WONER")
        ],
        [
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/cartoonfunny03'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/cartoonfunny03')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot!\n\nI can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup
    )

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await message.reply_text(f"{HELP_TXT}")

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await message.reply_text("**Batch Successfully Cancelled.**")

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        
        batch_temp.IS_BATCH[message.from_user.id] = False
        
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): 
                break
                
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                batch_temp.IS_BATCH[message.from_user.id] = True
                return
                
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
                await acc.start()
            except:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
            
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await message.reply(f"Error: {e}")
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await message.reply(f"Error: {e}")
            
            # public
            else:
                username = datas[3]
                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await message.reply("The username is not occupied by anyone")
                    return
                    
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id)
                except:
                    try:    
                        await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE:
                            await message.reply(f"Error: {e}")

            await asyncio.sleep(3)
            
        batch_temp.IS_BATCH[message.from_user.id] = True

# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    try:
        msg = await acc.get_messages(chatid, msgid)
    except:
        return
        
    if msg.empty: 
        return 
        
    msg_type = get_message_type(msg)
    if not msg_type: 
        return 
        
    if batch_temp.IS_BATCH.get(message.from_user.id): 
        return 
        
    if "Text" == msg_type:
        try:
            await message.reply_text(msg.text, entities=msg.entities, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE:
                await message.reply(f"Error: {e}")
            return 

    smsg = await message.reply_text('**Downloading...**')
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, message.chat.id))
    
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        if os.path.exists(f'{message.id}downstatus.txt'):
            os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE:
            await message.reply(f"Error: {e}")
        return await smsg.delete()
        
    if batch_temp.IS_BATCH.get(message.from_user.id): 
        return 
        
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, message.chat.id))

    caption = msg.caption if msg.caption else None
    if batch_temp.IS_BATCH.get(message.from_user.id): 
        return 
            
    try:
        if "Document" == msg_type:
            thumb = None
            if msg.document.thumbs:
                thumb = await acc.download_media(msg.document.thumbs[0].file_id)
            
            await message.reply_document(
                file, 
                thumb=thumb,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress, 
                progress_args=[message,"up"]
            )
            if thumb and os.path.exists(thumb):
                os.remove(thumb)

        elif "Video" == msg_type:
            thumb = None
            if msg.video.thumbs:
                thumb = await acc.download_media(msg.video.thumbs[0].file_id)
            
            await message.reply_video(
                file, 
                duration=msg.video.duration, 
                width=msg.video.width, 
                height=msg.video.height, 
                thumb=thumb,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress, 
                progress_args=[message,"up"]
            )
            if thumb and os.path.exists(thumb):
                os.remove(thumb)

        elif "Animation" == msg_type:
            await message.reply_animation(file)

        elif "Sticker" == msg_type:
            await message.reply_sticker(file)

        elif "Voice" == msg_type:
            await message.reply_voice(
                file, 
                caption=caption,
                caption_entities=msg.caption_entities,
                parse_mode=enums.ParseMode.HTML,
                progress=progress, 
                progress_args=[message,"up"]
            )

        elif "Audio" == msg_type:
            thumb = None
            if msg.audio.thumbs:
                thumb = await acc.download_media(msg.audio.thumbs[0].file_id)
            
            await message.reply_audio(
                file, 
                thumb=thumb,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress, 
                progress_args=[message,"up"]
            )
            if thumb and os.path.exists(thumb):
                os.remove(thumb)

        elif "Photo" == msg_type:
            await message.reply_photo(
                file, 
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
    
    except Exception as e:
        if ERROR_MESSAGE:
            await message.reply(f"Error: {e}")

    finally:
        # Cleanup
        if os.path.exists(f'{message.id}upstatus.txt'):
            os.remove(f'{message.id}upstatus.txt')
        if os.path.exists(file):
            os.remove(file)
        await smsg.delete()

# get the type of message
def get_message_type(msg):
    try:
        if msg.document:
            return "Document"
    except: pass

    try:
        if msg.video:
            return "Video"
    except: pass

    try:
        if msg.animation:
            return "Animation"
    except: pass

    try:
        if msg.sticker:
            return "Sticker"
    except: pass

    try:
        if msg.voice:
            return "Voice"
    except: pass

    try:
        if msg.audio:
            return "Audio"
    except: pass

    try:
        if msg.photo:
            return "Photo"
    except: pass

    try:
        if msg.text:
            return "Text"
    except: pass

    return None