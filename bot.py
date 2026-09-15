import asyncio
import logging
import os
import html
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatType
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Ошибка: Переменная BOT_TOKEN не найдена в Environment Variables!")

GROUP_ID = -1004394157854

bot = Bot(token=TOKEN)
dp = Dispatcher()

WELCOME_TEXT = (
    "      Чтобы вступить во флуд, заполните анкету и подпишитесь на каналы.\n"
    "Анкету можете найти в Инфо ➟ навигация ➟ вступление.\n"
    "Анкету отправляете боту.\n"
    "    ──────────\n"
    "        нᴀɯи ᴋᴀнᴀᴧы\n\n"
    "@SkylineAzure_INFO - инɸо ᴋᴀнᴀᴧ ɸᴧудᴀ\n\n"
    "@SkylineAzure_LIFE - ᴧᴀйɸ ᴋᴀнᴀᴧ ɸᴧудᴀ"
)

# 1. ОБРАБОТЧИК /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.answer(WELCOME_TEXT, parse_mode="HTML")

# 2. ОБРАБОТЧИК ВСЕХ ОСТАЛЬНЫХ СООБЩЕНИЙ
@dp.message()
async def handle_messages(message: types.Message):
    try:
        if message.text and message.text.strip().startswith("/start"):
            return

        # Если это личное сообщение боту
        if message.chat.type == ChatType.PRIVATE:
            user = message.from_user
            username = f" (@{user.username})" if user.username else ""
            
            # Заголовок с информацией о пользователе
            header_info = (
                f"📩 <b>Сообщение от пользователя:</b>\n"
                f"<b>Имя:</b> {user.full_name}{username}\n"
                f"<b>ID:</b> <code>{user.id}</code>\n"
                f"──────────"
            )

            # 1. Отправляем карточку пользователя в админ-группу
            await bot.send_message(chat_id=GROUP_ID, text=header_info, parse_mode="HTML")
            
            # 2. Копируем сообщение (сохраняет медиа, форматирование и премиум-эмодзи)
            await message.copy_to(chat_id=GROUP_ID)

            # 3. Отвечаем пользователю
            await message.reply("Спасибо! Ваше сообщение отправлено администраторам.")

        # Если админ отвечает в группе (через Reply)
        elif message.chat.id == GROUP_ID and message.reply_to_message:
            reply_msg = message.reply_to_message
            target_id = None
            
            target_text = reply_msg.text or reply_msg.caption or ""
            if "ID:" in target_text:
                try:
                    target_id = int(target_text.split("ID:")[1].split()[0].strip())
                except Exception:
                    pass

            if target_id:
                try:
                    await message.copy_to(chat_id=target_id)
                    await message.reply("✅ Ответ успешно отправлен!")
                except Exception as send_err:
                    # Уведомление об ошибке при ответе пользователю
                    error_msg = (
                        f"⚠️ <b>Ошибка при отправке ответа пользователю!</b>\n"
                        f"<b>ID пользователя:</b> <code>{target_id}</code>\n"
                        f"<b>Текст ошибки:</b> <code>{html.escape(str(send_err))}</code>"
                    )
                    await message.reply(error_msg, parse_mode="HTML")

    except Exception as e:
        logging.error(f"Error handling message: {e}")
        # Перехват глобальной ошибки при обработке входящей заявки
        try:
            user_info = ""
            if message.from_user:
                u = message.from_user
                user_info = f"\n<b>От пользователя:</b> {u.full_name} (@{u.username or 'без_юзернейма'}), ID: <code>{u.id}</code>"

            admin_error_alert = (
                f"❌ <b>Произошла ошибка при обработке сообщения!</b>{user_info}\n\n"
                f"<b>Детали ошибки:</b>\n<code>{html.escape(str(e))}</code>"
            )
            await bot.send_message(chat_id=GROUP_ID, text=admin_error_alert, parse_mode="HTML")
        except Exception as alert_err:
            logging.error(f"Failed to send error alert to group: {alert_err}")

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
