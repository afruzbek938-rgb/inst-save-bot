import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"
dp = Dispatcher()

async def download_video(url):
    # Video uchun eng oddiy sozlamalar
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "downloads/video.mp4",
        "quiet": True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return "downloads/video.mp4"
    except:
        return None

@dp.message(F.text.startswith("http"))
async def handle_url(msg: Message):
    wait_msg = await msg.reply("⏳ Yuklanmoqda...")
    file_path = await download_video(msg.text)
    
    if file_path and os.path.exists(file_path):
        await msg.reply_video(video=FSInputFile(file_path))
        os.remove(file_path)
        await wait_msg.delete()
    else:
        await wait_msg.edit_text("❌ Yuklashda xatolik yuz berdi.")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
