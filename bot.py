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

# Словарь соответствия Telegram ID администратора и имени его персонажа
ADMIN_PERSONAS = {
    1379515741: "Хелкарт",
    5825165518: "Ханаби",
    1389728660: "Селена",
    691127916: "Берелик",
    1324681606: "Кагура",
    7316096923: "Баданг",
    1406965637: "Ксавьер",
}

WELCOME_TEXT = (
    "Чтобы вступить во флуд, заполните анкету.\n"
    "Анкету можете найти в Инфо\n"
    "Инфо ➟ навигация ➟ вступление.\n\n"
    "             ────୨ৎ────\n\n"
    "              нᴀɯи ᴋᴀнᴀᴧы\n"
    "Подписка на каналы обязательна!\n"
    "@SkylineAzure_INFO - инɸо ᴋᴀнᴀᴧ ɸᴧудᴀ\n"
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
        # Если сообщение пришло в ЛС боту
        if message.chat.type == ChatType.PRIVATE:
            user = message.from_user
            username = f" (@{user.username})" if user.username else ""

            # 1. БЛОКИРОВКА НЕДОПУСТИМЫХ ТИПОВ КОНТЕНТА
            if message.sticker:
                await message.reply("Пожалуйста, не отправляйте стикеры — бот их не обрабатывает.")
                return
            if message.animation:
                await message.reply("Пожалуйста, не отправляйте гифки — бот их не обрабатывает.")
                return
            if message.photo:
                await message.reply("Пожалуйста, не отправляйте изображения — бот их не обрабатывает.")
                return
            if message.video or message.video_note:
                await message.reply("Пожалуйста, не отправляйте видео — бот их не обрабатывает.")
                return
            if message.document or message.voice or message.audio:
                await message.reply("Пожалуйста, отправляйте только текстовые сообщения.")
                return

            # 2. БЛОКИРОВКА ПРЕМИУМ-ЭМОДЗИ В ТЕКСТЕ
            entities = message.entities or message.caption_entities or []
            for entity in entities:
                if entity.type == "custom_emoji" or getattr(entity, "custom_emoji_id", None):
                    await message.reply("Пожалуйста, не отправляйте премиум-эмодзи — бот их не обрабатывает.")
                    return

            # 3. ОТПРАВКА ОБЫЧНОГО ТЕКСТА
            if message.text:
                username_line = f"<b>Юзер:</b> @{user.username}\n" if user.username else ""
                
                full_post = (
                    f"💌 <b>Пришло новое сообщение:</b>\n"
                    f"<b>Имя:</b> {html.escape(user.full_name)}\n"
                    f"{username_line}"
                    f"<b>ID:</b> <code>{user.id}</code>\n"
                    f"────୨ৎ────\n\n"
                    f"{html.escape(message.text)}"
                )
                await bot.send_message(chat_id=GROUP_ID, text=full_post[:4000], parse_mode="HTML")
                await message.reply("Ваше сообщение отправлено администраторам, ожидайте ответа! ｡𖦹°‧")

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
                    admin_id = message.from_user.id
                    persona_name = ADMIN_PERSONAS.get(admin_id, "Администратор")

                    # Если админ написал текст
                    if message.text:
                        formatted_response = (
                            f"<b>Ответ от {persona_name}:</b>\n\n"
                            f"{html.escape(message.text)}"
                        )
                        await bot.send_message(chat_id=target_id, text=formatted_response, parse_mode="HTML")
                        await message.reply("Успешно отправлено!")

                    # Если админ отправил фото с подписью
                    elif message.photo:
                        photo_file_id = message.photo[-1].file_id
                        caption_text = message.caption or ""
                        formatted_caption = (
                            f"<b>Ответ от {persona_name}:</b>\n\n"
                            f"{html.escape(caption_text)}"
                        )
                        await bot.send_photo(chat_id=target_id, photo=photo_file_id, caption=formatted_caption, parse_mode="HTML")
                        await message.reply("Успешно отправлено!")

                except Exception as send_err:
                    error_msg = (
                        f"⚠️ <b>Ошибка при отправке ответа пользователю!</b>\n"
                        f"<b>ID:</b> <code>{target_id}</code>\n"
                        f"<b>Ошибка:</b> <code>{html.escape(str(send_err))}</code>"
                    )
                    await message.reply(error_msg, parse_mode="HTML")

    except Exception as e:
        logging.error(f"Error handling message: {e}")
        try:
            if message and message.from_user:
                u = message.from_user
                username = f" (@{u.username})" if u.username else ""
                admin_error_alert = (
                    f"⚠️ <b>Не удалось переслать сообщение от пользователя из-за ошибки!</b>\n"
                    f"<b>Имя:</b> {html.escape(u.full_name)}{username}\n"
                    f"<b>ID:</b> <code>{u.id}</code>\n"
                    f"<b>Ошибка:</b> <code>{html.escape(str(e))}</code>"
                )
                await bot.send_message(chat_id=GROUP_ID, text=admin_error_alert, parse_mode="HTML")
        except Exception as alert_err:
            logging.error(f"Failed to send error alert: {alert_err}")

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
