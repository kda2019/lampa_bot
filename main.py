import logging
from aiogram import Bot, Dispatcher, executor, types
from settings import TOKEN
from actions import *

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(lambda message: message.chat.id != message.from_user.id and f"{message.from_user.id}_{message.chat.id}" in data, content_types=types.ContentType.ANY)
async def delete_message(message):
    """Удаляет все сообщения от админов, которые на данный момент находятся в муте"""
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(lambda message: message.chat.id != message.from_user.id)
async def group_messages(message):
    if message.text.split('@')[0] == '/eat_shawarma':
        await eat_shawarma(bot, message)
    elif message.text.split('@')[0] == '/check_my_lampovost':
        await check_my_lampovost(bot, message)
    elif message.text.split('@')[0] == '/check_top_lampovyh_cats':
        await check_top_lampovyh_cats(bot, message)
    elif message.reply_to_message is not None and message.text.split()[0].lower() == 'мут':
        await mute_user(bot, message)

@dp.message_handler(lambda message: message.chat.id == message.from_user.id)
async def group_messages(message):
    await bot.send_message(message.from_user.id, 'На данном этапе разработки я общаюсь только в ламповых чатиках :)')


executor.start_polling(dp)