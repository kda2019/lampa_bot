import random, datetime
from models import ChatModel, UserModel
from settings import TOKEN

async def eat_shawarma(bot, message):
    """Игра в которой юзер может получить +5, +2 или -3 к ламповости раз в 4 часа"""
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    if datetime.datetime.now() - user.last_shava < datetime.timedelta(hours=4):
        await bot.send_message(message.chat.id, 'Ты недавно уже кушал, пока хватит.', reply_to_message_id=message.message_id)
    else:
        r = random.randint(1, 3)
        if r == 1:
            user.amount += 5
            await bot.send_message(message.chat.id, 'Сладкая сочная шаурма. Пальчики оближешь. +5 к ламповости', reply_to_message_id=message.message_id)
        elif r == 2:
            user.amount += 2
            await bot.send_message(message.chat.id, 'Сносная шавуха. Ты утолил свой голод. +2 к ламповости', reply_to_message_id=message.message_id)
        else:
            user.amount += -3
            await bot.send_message(message.chat.id, 'Придя домой ты знатно проблевался. -3 к ламповости', reply_to_message_id=message.message_id)
        user.last_shava = datetime.datetime.now()
        user.save()


async def check_my_lampovost(bot, message):
    """Выводит ламповость юзера в текущем чате"""
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    await bot.send_message(message.chat.id, f'Твоя ламповость "{user.amount}"', reply_to_message_id=message.message_id)


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
    if (await bot.get_chat_member(message.chat.id, TOKEN.split(':')[0])).status != "administrator":
        await bot.send_message(message.chat.id, 'Я не смогу это сделать пока не стану админом :(', reply_to_message_id=message.message_id)

    elif message.reply_to_message.from_user.is_bot:
        await bot.send_message(message.chat.id, 'Зачем ты пытаешься поразить бота? Он бесчувственный пустой мешок нулей и единиц', reply_to_message_id=message.message_id)

    elif (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status in ["administrator", "creator"]:
        await bot.send_message(message.chat.id, f"Наши админы настолько ламповые, что круглосуточно восхищаются сами собой. Тебе не удалось поразить {message.reply_to_message.from_user.first_name}", reply_to_message_id=message.message_id)

    else:
        user = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0], user_id=message.from_user.id)[0]
        max_time_mute = user.amount ** (1 / 2)

        try:
            time_mute = int(message.text.split()[1])
        except:
            time_mute = max_time_mute

        if time_mute > max_time_mute:
            time_mute = max_time_mute
        elif time_mute < 1:
            await bot.send_message(message.chat.id, 'Вы недостаточно ламповы чтобы кого-то замутить :(', reply_to_message_id=message.message_id)
            return

        if (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status == "restricted":
            await bot.send_message(message.chat.id, f'{message.reply_to_message.from_user.first_name} уже поражен и не может сказать ни слова.', reply_to_message_id=message.message_id)

        else:
            dt_mute = datetime.timedelta(minutes=time_mute)
            await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=dt_mute)
            await bot.send_message(message.chat.id, f'{message.from_user.first_name} поразил своей ламповостью кота по имени {message.reply_to_message.from_user.first_name}.\n{message.reply_to_message.from_user.first_name} восхищен и не сможет сказать ни слова {dt_mute.seconds//60} мин. {dt_mute.seconds%60} сек.', reply_to_message_id=message.message_id)
            user.amount -= int(time_mute)
            user.save()


