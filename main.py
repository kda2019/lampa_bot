import logging
from aiogram import Bot, Dispatcher, executor, types
from settings import TOKEN
from actions import *

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)


# Этот хендлер отвечает за удаление всех сообщений от админов находящихся в муте
@dp.message_handler(lambda message:f"{message.from_user.id}_{message.chat.id}" in data, content_types=types.ContentType.ANY)
async def delete_message(message):
    await bot.delete_message(message.chat.id, message.message_id)


# Хендлеры ниже отвечают за команды в общем чате
@dp.message_handler(commands=['eat_shawarma'])
async def eat_shawarma_handler(message):
    if message.chat.id != message.from_user.id:
        await eat_shawarma(bot, message)


@dp.message_handler(commands=['check_my_lampovost'])
async def check_my_lampovost_handler(message):
    if message.chat.id != message.from_user.id:
        await check_my_lampovost(bot, message)


@dp.message_handler(commands=['check_top_lampovyh_cats'])
async def check_top_lampovyh_cats_handler(message):
    if message.chat.id != message.from_user.id:
        await mute_user(bot, message)


@dp.message_handler(commands=['smoke_kalik'])
async def smoke_kalik_handler(message):
    if message.chat.id != message.from_user.id:
        await smoke_kalik(bot, message)


# Хендлеры ниже отвечают за команды в личном чате бота
@dp.message_handler(commands=['start'])
async def start_handler(message):
    if message.chat.id == message.from_user.id:
        await start(bot, message)


@dp.message_handler(commands=['help'])
async def help_handler(message):
    if message.chat.id == message.from_user.id:
        await help(bot, message)


@dp.message_handler(lambda message: message.chat.id != message.from_user.id)
async def group_messages_handler(message):
    if message.reply_to_message is not None and message.text.split()[0].lower() == 'мут':
        await mute_user(bot, message)

#Хендлеры ниже отвечают за колбеки
@dp.callback_query_handler()
async def join_kalik_handler(call):
    await join_to_kalik(bot, call)



executor.start_polling(dp)