import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

# Bot tokennni shu yerga yozing
TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"

dp = Dispatcher()
user_data = {}

TEXTS = {
    'uz': {
        'welcome': "👋 *InstaTubeBot-ga xush kelibsiz!*\n\n📥 Havolani yuboring, men video yoki musiqani yuklab beraman.",
        'btn_video_mode': "📥 VIDEO YUKLASH",
        'btn_lang': "🌐 TILNI O'ZGARTIRISH",
        'prompt_video': "👇 Havolani yuboring:",
        'error': "⚠️ Xatolik: Havolani tekshiring.",
        'remind': "💡 Iltimos, havolani yuboring!"
    },
    'ru': {
        'welcome': "👋 *Добро пожаловать в InstaTubeBot!*\n\n📥 Отправьте ссылку, и я скачаю видео или аудио.",
        'btn_video_mode': "📥 СКАЧАТЬ ВИДЕО",
        'btn_lang': "🌐 СМЕНИТЬ ЯЗЫК",
        'prompt_video': "👇 Отправьте ссылку:",
        'error': "⚠️ Ошибка: Проверьте ссылку.",
        'remind': "💡 Пожалуйста, отправьте ссылку!"
    },
    'en': {
        'welcome': "👋 *Welcome to InstaTubeBot!*\n\n📥 Send me a link, and I will download the video or audio.",
        'btn_video_mode': "📥 DOWNLOAD VIDEO",
        'btn_lang': "🌐 CHANGE LANGUAGE",
        'prompt_video': "👇 Send the link:",
        'error': "⚠️ Error: Check the link.",
        'remind': "💡 Please, send a link!"
    }
}

# Yuklash sozlamalari
YDL_OPTS = {
    "format": "best[ext=mp4]/best",
    "quiet": True,
    "nocheckcertificate": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

async def download_media(url, is_audio=False):
    opts = YDL_OPTS.copy()
    if is_audio:
        opts["format"] = "bestaudio/best"
        opts["outtmpl"] = "downloads/audio.%(ext)s"
    else:
        opts["outtmpl"] = "downloads/video.%(ext)s"
        
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info
    except: return None

# --- Tugmalar ---
def get_main_keyboard(lang):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[lang]['btn_video_mode'])], [KeyboardButton(text=TEXTS[lang]['btn_lang'])]], resize_keyboard=True)

def get_lang_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)

# --- Handlers ---
@dp.message(F.text == "/start")
async def start(msg: Message):
    await msg.reply("Tilni tanlang / Выберите язык / Select language:", reply_markup=get_lang_keyboard())

@dp.message(F.text.in_({"🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"}))
async def set_lang(msg: Message):
    lang = {'🇺🇿 O'zbekcha': 'uz', '🇷🇺 Русский': 'ru', '🇬🇧 English': 'en'}[msg.text]
    user_data[msg.chat.id] = lang
    await msg.reply(TEXTS[lang]['welcome'], reply_markup=get_main_keyboard(lang), parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text.contains("http"))
async def handle_url(msg: Message):
    lang = user_data.get(msg.chat.id, 'uz')
    wait = await msg.reply("⏳ *Yuklanmoqda...*", parse_mode=ParseMode.MARKDOWN)
    
    info = await download_media(msg.text)
    if info:
        path = f"downloads/video.{info.get('ext', 'mp4')}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎵 MP3", callback_data=f"mp3_{msg.text}")]])
        await msg.reply_video(video=FSInputFile(path), caption=f"📹 *{info['title']}*", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        os.remove(path)
        await wait.delete()
    else:
        await wait.edit_text(TEXTS[lang]['error'])

@dp.callback_query(F.data.startswith("mp3_"))
async def send_mp3(call: CallbackQuery):
    url = call.data.split("_", 1)[1]
    info = await download_media(url, is_audio=True)
    if info:
        path = f"downloads/audio.{info.get('ext', 'mp3')}"
        await call.message.reply_audio(audio=FSInputFile(path), title=info['title'])
        os.remove(path)
    await call.answer()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
