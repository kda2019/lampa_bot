import random, datetime
from models import ChatModel, UserModel


async def eat_shawarma(bot, message):
    """Игра в которой юзер может получить +5, +2 или -4 к ламповости раз в 4 часа"""
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    if datetime.datetime.now() - user.last_shava < datetime.timedelta(hours=4):
        await bot.send_message(message.chat.id, 'Ты недавно уже кушал, пока хватит.')
    else:
        r = random.randint(1, 3)
        if r == 1:
            user.amount += 5
            await bot.send_message(message.chat.id, 'Сладкая сочная шаурма. Пальчики оближешь. +5 к ламповости')
        elif r == 2:
            user.amount += 2
            await bot.send_message(message.chat.id, 'Сносная шавуха. Ты утолил свой голод. +2 к ламповости')
        else:
            user.amount += -4
            await bot.send_message(message.chat.id, 'Придя домой ты знатно проблевался. -4 к ламповости')
        user.last_shava = datetime.datetime.now()
        user.save()


async def check_my_lampovost(bot, message):
    """Выводит ламповость юзера в текущем чате"""
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    await bot.send_message(message.chat.id, f'Твоя ламповость "{user.amount}"')


async def check_top_lampovyh_cats(bot, message):
    """Выводит топ 20 юзеров в текущем чате"""
    chat, _ = ChatModel.get_or_create(chat_id=message.chat.id)
    text = 'Топ ламповых котов этого чата:\n\n'
    users = chat.usermodel_set.order_by('amount')
    counter = 1
    for i in users:
        if counter > 20:
            break
        user_ = await bot.get_chat_member(message.chat.id, i.user_id)
        text += f"{counter}) <a href='tg://user?id={i.user_id}'>{user_.user.first_name} </a> - {i.amount}\n"
        counter += 1
    await bot.send_message(message.chat.id, text, parse_mode='HTML')
