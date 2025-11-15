# Don't Remove Credit Tg - @RS_WONER
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@RS_WONER
# Ask Doubt on telegram @RS_WONER

import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        await message.reply("**You are not logged in!**")
        return 
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successfully** ✅")

@Client.on_message(filters.private & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**You are already logged in. First /logout your old session, then login again.**")
        return 
        
    user_id = message.from_user.id
    try:
        phone_number_msg = await bot.ask(
            chat_id=user_id, 
            text="**Please send your phone number with country code:**\n\nExample: `+13124562345` or `+9171828181889`\n\nSend /cancel to cancel.",
            timeout=300
        )
    except TimeoutError:
        await message.reply("**Time out! Please try again.**")
        return
        
    if phone_number_msg.text == '/cancel':
        return await phone_number_msg.reply('**Process cancelled!**')
        
    phone_number = phone_number_msg.text.strip()
    
    await phone_number_msg.reply("**Sending OTP...**")
    
    try:
        client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)
        await client.connect()
        code = await client.send_code(phone_number)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('**Phone number is invalid.**')
        return
    except Exception as e:
        await phone_number_msg.reply(f'**Error:** `{e}`')
        return

    try:
        phone_code_msg = await bot.ask(
            user_id, 
            "**Please check your Telegram app for OTP and send it here:**\n\nIf OTP is `12345`, send as: `1 2 3 4 5`\n\nSend /cancel to cancel.", 
            filters=filters.text, 
            timeout=600
        )
    except TimeoutError:
        await message.reply("**Time out! Please try again.**")
        return
        
    if phone_code_msg.text == '/cancel':
        return await phone_code_msg.reply('**Process cancelled!**')
        
    phone_code = phone_code_msg.text.replace(" ", "")
    
    try:
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**OTP is invalid.**')
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**OTP is expired.**')
        return
    except SessionPasswordNeeded:
        try:
            two_step_msg = await bot.ask(
                user_id, 
                '**Your account has two-step verification. Please provide your password:**\n\nSend /cancel to cancel.', 
                filters=filters.text, 
                timeout=300
            )
        except TimeoutError:
            await message.reply("**Time out! Please try again.**")
            return
            
        if two_step_msg.text == '/cancel':
            return await two_step_msg.reply('**Process cancelled!**')
            
        try:
            await client.check_password(two_step_msg.text)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Invalid password!**')
            return
    
    string_session = await client.export_session_string()
    await client.disconnect()
    
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('**Invalid session string generated!**')
    
    try:
        await db.set_session(message.from_user.id, session=string_session)
        await message.reply("**✅ Login Successful!**\n\nYou can now download restricted content.")
    except Exception as e:
        await message.reply(f"**Error saving session:** `{e}`")