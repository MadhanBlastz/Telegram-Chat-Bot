import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = "7622386339:AAF-Stwm65pxl1V8654FgmtEE7VQTm3f1pE"
ADMIN_ID = 2021408974  # Replace with your actual Telegram user ID
ADMIN_ICON = "👑 Admin"  # Display name for admin messages

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Store active users
users = set()


@dp.message(Command("start"))
async def start(message: types.Message):
    users.add(message.chat.id)
    await message.answer("Welcome! This is a public chat. Everyone can see messages. Admin messages will be shared to all users.")


@dp.message(Command("leave"))
async def leave(message: types.Message):
    users.discard(message.chat.id)
    await message.answer("You have left the chat. Send /start to rejoin.")


async def broadcast_message(sender_id, content_func, *args, **kwargs):
    """Send messages to all users except the sender."""
    for user_id in users:
        if user_id == sender_id:
            continue
        try:
            await content_func(user_id, *args, **kwargs)
        except:
            pass


@dp.message(F.text)
async def broadcast_text(message: types.Message):
    """Send admin messages and user messages to everyone except sender."""
    sender_name = ADMIN_ICON if message.chat.id == ADMIN_ID else message.from_user.first_name
    text = f"{sender_name}: {message.text}"

    # Send to everyone except the sender
    await broadcast_message(message.chat.id, bot.send_message, text)


async def handle_media(message: types.Message, media_type: str):
    """Handles media messages (photo, video, sticker, document)"""
    sender_name = ADMIN_ICON if message.chat.id == ADMIN_ID else message.from_user.first_name
    caption = f"{sender_name}: {message.caption}" if message.caption else sender_name

    # Choose send function
    if media_type == "photo":
        send_func = bot.send_photo
        file_id = message.photo[-1].file_id
    elif media_type == "video":
        send_func = bot.send_video
        file_id = message.video.file_id
    elif media_type == "sticker":
        send_func = bot.send_sticker
        file_id = message.sticker.file_id
    elif media_type == "document":
        send_func = bot.send_document
        file_id = message.document.file_id
    else:
        return

    # Send to all except sender
    await broadcast_message(message.chat.id, send_func, file_id, caption=caption)


@dp.message(F.photo)
async def broadcast_photo(message: types.Message):
    await handle_media(message, "photo")


@dp.message(F.video)
async def broadcast_video(message: types.Message):
    await handle_media(message, "video")


@dp.message(F.sticker)
async def broadcast_sticker(message: types.Message):
    await handle_media(message, "sticker")


@dp.message(F.document)
async def broadcast_document(message: types.Message):
    await handle_media(message, "document")


async def main():
    """Start bot with polling."""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
