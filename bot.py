import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatType
from aiogram.filters import CommandStart

TOKEN = "8617801757:AAHg2OAGh0Rh8aefbPmQxeKML0tUWTJRsrY"
GROUP_ID = -1004394157854

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    if message.chat.type == ChatType.PRIVATE:
        welcome_text = (
            "Добро пожаловать в <b>𝐒𝐤𝐲𝐥𝐢𝐧𝐞 𝐀𝐳𝐮𝐫𝐞 𖤓</b>\n"
            "──────────\n"
            "Чтобы вступить во флуд, заполните анкету и подпишитесь на каналы.\n"
            "Анкету можете найти в Инфо ➟ навигация ➟ вступление.\n"
            "Анкету отправляете боту.\n"
            "──────────\n"
            "нᴀɯи ᴋᴀнᴀᴧы\n\n"
            "@SkylineAzure_INFO - инɸо ᴋᴀнᴀᴧ ɸᴧудᴀ\n"
            "@SkylineAzure_LIFE - ᴧᴀйɸ ᴋᴀнᴀᴧ ɸᴧудᴀ"
        )
        await message.answer(welcome_text, parse_mode="HTML")

# Обработчик сообщений пользователей и ответов админов
@dp.message()
async def handle_messages(message: types.Message):
    try:
        # ЛС с пользователем -> отправка в группу админов
        if message.chat.type == ChatType.PRIVATE:
            user = message.from_user
            username = f" (@{user.username})" if user.username else ""
            text = f"📩 <b>Сообщение от пользователя:</b>\n" \
                   f"<b>Имя:</b> {user.full_name}{username}\n" \
                   f"<b>ID:</b> <code>{user.id}</code>\n\n" \
                   f"<b>Текст:</b>\n{message.text or '[Медиафайл/Вложение]'}"
            
            await bot.send_message(chat_id=GROUP_ID, text=text, parse_mode="HTML")
            await message.reply("Спасибо! Ваше сообщение отправлено администраторам.")

        # Ответ админа в группе (через Reply) -> отправка пользователю
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
