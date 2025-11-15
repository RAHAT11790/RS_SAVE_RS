# Don't Remove Credit Tg - @RS_WONER
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@RS_WONER
# Ask Doubt on telegram @RS_WONER

from pyrogram.errors import InputUserDeactivated, FloodWait, UserIsBlocked, PeerIdInvalid
from database.db import db
from pyrogram import Client, filters
from config import ADMINS
import asyncio
import datetime
import time

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        return False, "Error"

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text("**Please reply to a message to broadcast.**")
    
    sts = await message.reply_text("**📢 Starting Broadcast...**")
    
    start_time = time.time()
    total_users = await db.total_users_count()
    users = await db.get_all_users()
    
    done = 0
    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    for user in users:
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success += 1
        else:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
                
        done += 1
        
        if done % 20 == 0:
            try:
                await sts.edit(
                    f"**Broadcast Progress:**\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done}/{total_users}\n"
                    f"Success: {success}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}\n"
                    f"Failed: {failed}"
                )
            except:
                pass
    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    
    await sts.edit(
        f"**📊 Broadcast Completed!**\n\n"
        f"Time Taken: {time_taken}\n"
        f"Total Users: {total_users}\n"
        f"Success: {success}\n"
        f"Blocked: {blocked}\n"
        f"Deleted: {deleted}\n"
        f"Failed: {failed}"
    )