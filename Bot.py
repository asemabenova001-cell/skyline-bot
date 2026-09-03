import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatType

TOKEN = "8617801757:AAHg2OAGh0Rh8aefbPmQxeKML0tUWTJRsrY"
GROUP_ID = -1004394157854

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_messages(message: types.Message):
try:
if message.chat.type == ChatType.PRIVATE:
user = message.from_user
username = f" (@{user.username})" if user.username else ""

info_text = (
f"📩 Новое сообщение из ЛС!\n"
f"👤 От: {user.full_name}{username}\n"
f"🆔 ID: {user.id}\n"
f"💬 Текст: {message.text or '[Медиа/Файл]'}\n"
f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
f"✍️ Чтобы ответить пользователю, свайпните (сделайте Reply) НА ЭТО СООБЩЕНИЕ!"
)

await bot.send_message(chat_id=GROUP_ID, text=info_text)
if not message.text:
await message.forward(chat_id=GROUP_ID)
await message.reply("✅ Ваше сообщение отправлено администраторам!")

elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
if message.reply_to_message:
reply_text = message.reply_to_message.text or ""
if "🆔 ID: " in reply_text:
try:
target_id = int(reply_text.split("🆔 ID: ")[1].split("\n")[0])
reply_content = message.text or message.caption or "[Медиа/Файл]"

await bot.send_message(
chat_id=target_id,
text=f"💬 Ответ администратора:\n{reply_content}"
)
await message.reply("✅ Ответ отправлен пользователю в ЛС!")
except Exception as err:
await message.reply("⚠️ Не удалось отправить ответ.")
except Exception as e:
print(f"Ошибка: {e}")

async def main():
await bot.delete_webhook(drop_pending_updates=True)
await dp.start_polling(bot)

if name == "main":
logging.basicConfig(level=logging.INFO)
asyncio.run(main())