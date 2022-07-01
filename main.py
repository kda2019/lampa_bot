import logging
from aiogram import Bot, Dispatcher, executor, types

from lampa_bot.prototype_actions import EatShawarmaStrategy

from actions import *
from settings import TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)


# Этот хендлер отвечает за удаление всех сообщений от админов находящихся в муте
@dp.message_handler(lambda message: f"{message.from_user.id}_{message.chat.id}" in muted_admins,
                    content_types=types.ContentType.ANY)
async def delete_message(message):
    await bot.delete_message(message.chat.id, message.message_id)


# Хендлеры ниже отвечают за команды в общем чате
@dp.message_handler(commands=['eat_shawarma'])
async def eat_shawarma_handler(message):
    if message.chat.id != message.from_user.id:
        await EatShawarmaStrategy(bot, message).start_eat_shawarma()


@dp.message_handler(commands=['check_my_lampovost'])
async def check_my_lampovost_handler(message):
    if message.chat.id != message.from_user.id:
        await check_my_lampovost(bot, message)


@dp.message_handler(commands=['check_top_lampovyh_cats'])
async def check_top_lampovyh_cats_handler(message):
    if message.chat.id != message.from_user.id:
        await check_top_lampovyh_cats(bot, message)


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


# Хендлеры ниже отвечают за колбеки
@dp.callback_query_handler()
async def callbacks(call):
    if call.data.startswith('eating_now'):
        await EatShawarmaStrategy.eat_shawarma_call(bot, call)
    elif call.data == 'join_kalik':
        await join_to_kalik(bot, call)


executor.start_polling(dp)
