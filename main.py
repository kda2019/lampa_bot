import logging
from aiogram import Bot, Dispatcher, executor
from settings import TOKEN
from actions import *

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)

data = {}


@dp.message_handler(lambda message: message.chat.id != message.from_user.id)
async def group_messages(message):
    if message.text == '/eat_shawarma':
        await eat_shawarma(bot, message)
    elif message.text == '/check_my_lampovost':
        await check_my_lampovost(bot, message)
    elif message.text == '/check_top_lampovyh_cats':
        await check_top_lampovyh_cats(bot, message)
    elif message.reply_to_message is not None and message.text.split()[0].lower() == 'мут':
        await mute_user(bot, message)

@dp.message_handler(lambda message: message.chat.id == message.from_user.id)
async def group_messages(message):
    await bot.send_message(message.from_user.id, 'На данном этапе разработки я общаюсь только в ламповых чатиках :)')


executor.start_polling(dp)
