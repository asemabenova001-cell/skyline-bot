import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatType
from aiogram.filters import Command

TOKEN = "8617801757:AAHg2OAGh0Rh8aefbPmQxeKML0tUWTJRsrY"
GROUP_ID = -1004394157854

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Текст приветствия
WELCOME_TEXT = (
    "      Чтобы вступить во флуд, заполните анкету и подпишитесь на каналы.\n"
    "Анкету можете найти в Инфо ➟ навигация ➟ вступление.\n"
    "Анкету отправляете боту.\n"
    "    ──────────\n"
    "        нᴀɯи ᴋᴀнᴀᴧы\n\n"
    "@SkylineAzure_INFO - инɸо ᴋᴀнᴀᴧ ɸᴧудᴀ\n\n"
    "@SkylineAzure_LIFE - ᴧᴀйɸ ᴋᴀнᴀᴧ ɸᴧудᴀ"
)

# 1. ОБРАБОТЧИК КОМАНДЫ /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.answer(WELCOME_TEXT, parse_mode="HTML")

# 2. ОБРАБОТЧИК ВСЕХ ОСТАЛЬНЫХ СООБЩЕНИЙ
@dp.message()
async def handle_messages(message: types.Message):
    try:
        # Пропускаем команду /start, если она попала сюда
        if message.text and message.text.strip().startswith("/start"):
            return

        # Если это личное сообщение боту
        if message.chat.type == ChatType.PRIVATE:
            user = message.from_user
            username = f" (@{user.username})" if user.username else ""
            text = (
                f"📩 <b>Сообщение от пользователя:</b>\n"
                f"<b>Имя:</b> {user.full_name}{username}\n"
                f"<b>ID:</b> <code>{user.id}</code>\n\n"
                f"<b>Текст:</b>\n{message.text or '[Медиафайл/Вложение]'}"
            )
            
            await bot.send_message(chat_id=GROUP_ID, text=text, parse_mode="HTML")
            await message.reply("Спасибо! Ваше сообщение отправлено администраторам.")

        # Если админ отвечает в группе (через Reply)
        elif message.chat.id == GROUP_ID and message.reply_to_message:
            reply_text = message.reply_to_message.text or ""
            if "ID:" in reply_text:
                try:
                    target_id = int(reply_text.split("ID:")[1].split()[0].strip())
                    await bot.send_message(
                        chat_id=target_id,
                        text=f"💬 <b>Ответ от администратора:</b>\n\n{message.text}",
                        parse_mode="HTML"
                    )
                    await message.reply("✅ Ответ успешно отправлен!")
                except Exception as e:
                    await message.reply(f"❌ Ошибка отправки: {e}")
    except Exception as e:
        logging.error(f"Error handling message: {e}")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
