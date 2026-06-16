import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import yt_dlp

TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"
dp = Dispatcher()

# Yuklash sozlamalari (Crashed bo'lmasligi uchun xavfsiz qilib yozildi)
def get_ydl_opts(is_audio=False):
    return {
        "format": "bestaudio/best" if is_audio else "best[ext=mp4]/best",
        "quiet": True,
        "nocheckcertificate": True,
        "outtmpl": "downloads/temp.%(ext)s",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

async def download_media(query, is_audio=False):
    ydl_opts = get_ydl_opts(is_audio)
    ydl_opts["default_search"] = "ytsearch1:"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query} official audio", download=True)
            return info['entries'][0] if 'entries' in info else None
    except Exception as e:
        print(f"Download Error: {e}")
        return None

@dp.message(F.text == "/start")
async def start(msg: Message):
    await msg.reply("Salom! Qo'shiq nomini yozing:")

@dp.message(F.text)
async def handle_text(msg: Message):
    wait = await msg.reply("⏳ Qidirilmoqda...")
    info = await download_media(msg.text, is_audio=True)
    if info:
        path = f"downloads/temp.{info.get('ext', 'mp3')}"
        await msg.reply_audio(audio=FSInputFile(path), title=info.get('title', 'Audio'), caption="@Mucis_Saved_bot")
        os.remove(path)
        await wait.delete()
    else:
        await wait.edit_text("❌ Topilmadi, boshqa nom bilan urinib ko'ring.")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
