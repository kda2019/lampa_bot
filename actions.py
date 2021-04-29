import random, datetime
from models import ChatModel, UserModel
from settings import TOKEN
from asyncio import sleep

data = []


async def eat_shawarma(bot, message):
    """Игра в которой юзер может получить +5, +2 или -3 к ламповости раз в 4 часа"""
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    if datetime.datetime.now() - user.last_shava < datetime.timedelta(hours=4):
        await bot.send_message(message.chat.id, 'Ты недавно уже кушал(а), пока хватит.', reply_to_message_id=message.message_id)
    else:
        r = random.randint(1, 3)
        if r == 1:
            user.amount += 5
            await bot.send_message(message.chat.id, 'Сладкая сочная шаурма. Пальчики оближешь. +5 к ламповости', reply_to_message_id=message.message_id)
        elif r == 2:
            user.amount += 2
            await bot.send_message(message.chat.id, 'Сносная шавуха. Ты утолил(а) свой голод. +2 к ламповости', reply_to_message_id=message.message_id)
        else:
            user.amount += -3
            await bot.send_message(message.chat.id, 'Придя домой ты знатно проблевался. -3 к ламповости', reply_to_message_id=message.message_id)
        user.last_shava = datetime.datetime.now()
        user.save()


async def check_my_lampovost(bot, message):
    """Выводит ламповость юзера в текущем чате"""
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    await bot.send_message(message.chat.id, f'Твоя ламповость:  {user.amount}', reply_to_message_id=message.message_id)


async def check_top_lampovyh_cats(bot, message):
    """Выводит топ 20 юзеров в текущем чате"""
    chat, _ = ChatModel.get_or_create(chat_id=message.chat.id)
    text = 'Топ ламповых котов этого чата:\n\n'
    users = chat.usermodel_set.order_by(-UserModel.amount)
    counter = 1
    for i in users:
        if counter > 20:
            break
        user_ = await bot.get_chat_member(message.chat.id, i.user_id)
        text += f"{counter}) {user_.user.first_name}:  {i.amount}\n"
        counter += 1
    await bot.send_message(message.chat.id, text)


async def mute_user(bot, message):
    """ Мутит юзера указанного в message.reply_to_message.from_user.id на время подсчитанное по формуле sqrt(UserModel.amount)
    Если приходит запрос на мут адина, то вместо мута будут моментально удалятся все сообщения написанные админом.
    """
    if (await bot.get_chat_member(message.chat.id, TOKEN.split(':')[0])).status != "administrator":  # Если у бота нет прав администратора
        await bot.send_message(message.chat.id, 'Я не смогу это сделать пока не стану админом :(', reply_to_message_id=message.message_id)

    elif message.reply_to_message.from_user.is_bot:  # Если целью мута является бот
        await bot.send_message(message.chat.id, 'Зачем ты пытаешься поразить бота? Он бесчувственный пустой мешок нулей и единиц.', reply_to_message_id=message.message_id)

    else:
        user = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0], user_id=message.from_user.id)[0]
        max_time_mute = user.amount ** (1 / 2)
        try:
            time_mute = int(message.text.split()[1])
            if time_mute < 1:
                await bot.send_message(message.chat.id, 'Время мута не должно быть меньше 1.', reply_to_message_id=message.message_id)
                return  # Если время мута зададут как 0 или отрицательное число, то бот никак не отреагирует
        except (IndexError, ValueError):
            time_mute = max_time_mute
        if time_mute > max_time_mute:
            time_mute = max_time_mute
        dt_mute = datetime.timedelta(minutes=time_mute)
        # Выше происходит расчет времени мута
        if time_mute < 1:
            await bot.send_message(message.chat.id, 'Вы недостаточно ламповы чтобы кого-то замутить :(', reply_to_message_id=message.message_id)

        elif (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status == "restricted" or f"{message.reply_to_message.from_user.id}_{message.chat.id}" in data:  # Если цель мута уже ограничена
            await bot.send_message(message.chat.id, f'{message.reply_to_message.from_user.first_name} уже поражен(а) и не может сказать ни слова.', reply_to_message_id=message.message_id)

        elif (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status in ["administrator", "creator"]:  # Если целью мута является админ
            await bot.send_message(message.chat.id, f"Наши админы настолько ламповые, что круглосуточно восхищаются сами собой. Но всё-же тебе удалось поразить админа по имени {message.reply_to_message.from_user.first_name}.\n{message.reply_to_message.from_user.first_name} восхищен(а) и не сможет сказать ни слова {dt_mute.seconds//60} мин. {dt_mute.seconds%60} сек.", reply_to_message_id=message.message_id)
            data.append(f"{message.reply_to_message.from_user.id}_{message.chat.id}")
            user.amount -= int(time_mute)
            user.save()
            await sleep(time_mute * 60)
            data.remove(f"{message.reply_to_message.from_user.id}_{message.chat.id}")

        else:  # Если целью мута является обычный пользователь
            await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=dt_mute)
            await bot.send_message(message.chat.id, f'{message.from_user.first_name} поразил своей ламповостью кота по имени {message.reply_to_message.from_user.first_name}.\n{message.reply_to_message.from_user.first_name} восхищен(а) и не сможет сказать ни слова {dt_mute.seconds//60} мин. {dt_mute.seconds%60} сек.', reply_to_message_id=message.message_id)
            user.amount -= int(time_mute)
            user.save()