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
    x = await bot.get_chat(message.from_user.id)
    print(x)
    if message.text == '/eat_shawarma':
        await eat_shawarma(bot, message)
    if message.text == '/check_my_lampovost':
        await check_my_lampovost(bot, message)
    if message.text == '/check_top_lampovyh_cats':
        await check_top_lampovyh_cats(bot, message)
    if message.text == '/test':
        x = await bot.get_chat_member(message.chat.id, message.from_user.id)
        print(x.user.first_name)
        caption = f"<a href='tg://user?id={message.from_user.id}'>{x.user.first_name} </a> - Красавчик"
        await bot.send_message(message.chat.id, caption, parse_mode='HTML')


@dp.message_handler(lambda message: message.chat.id == message.from_user.id)
async def group_messages(message):
    await bot.send_message(message.from_user.id, 'На данном этапе разработки я общаюсь только в ламповых чатиках :)')


executor.start_polling(dp)
