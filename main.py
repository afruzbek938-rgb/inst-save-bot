import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"
dp = Dispatcher()
user_data = {}

# Til sozlamalari
TEXTS = {
    'uz': {'welcome': "👋 *Salom! InstaTubeBot-ga xush kelibsiz!*\n\n📥 Havolani yuboring.", 'btn_video': "📥 VIDEO YUKLASH", 'error': "⚠️ Xatolik."},
    'ru': {'welcome': "👋 *Добро пожаловать в InstaTubeBot!*\n\n📥 Отправьте ссылку.", 'btn_video': "📥 СКАЧАТЬ ВИДЕО", 'error': "⚠️ Ошибка."},
    'en': {'welcome': "👋 *Welcome to InstaTubeBot!*\n\n📥 Send me a link.", 'btn_video': "📥 DOWNLOAD VIDEO", 'error': "⚠️ Error."}
}

async def download_media(url):
    ydl_opts = {"format": "best[ext=mp4]/best", "outtmpl": "downloads/vid.mp4", "quiet": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info if info else None
    except: return None

@dp.message(F.text == "/start")
async def start(msg: Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)
    await msg.reply("Tilni tanlang:", reply_markup=kb)

@dp.message(F.text.in_({"🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"}))
async def set_lang(msg: Message):
    lang = {'🇺🇿 O'zbekcha': 'uz', '🇷🇺 Русский': 'ru', '🇬🇧 English': 'en'}[msg.text]
    user_data[msg.chat.id] = lang
    await msg.reply(TEXTS[lang]['welcome'])

@dp.message(F.text.contains("http"))
async def handle_url(msg: Message):
    info = await download_media(msg.text)
    if info:
        await msg.reply_video(video=FSInputFile("downloads/vid.mp4"), caption=info['title'])
        os.remove("downloads/vid.mp4")
    else:
        await msg.reply("Xatolik yuz berdi.")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
