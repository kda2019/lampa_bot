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


async def mute_user(bot, message):
    if (await bot.get_chat_member(message.chat.id, 954054488)).status != "administrator":
        await bot.send_message(message.chat.id, 'Я не смогу это сделать пока не стану админом :(')

    elif message.reply_to_message.from_user.is_bot:
        await bot.send_message(message.chat.id, 'Зачем ты пытаешься поразить бота? Он бесчувственный пустой мешок нулей и единиц')

    elif (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status in ["administrator", "creator"]:
        await bot.send_message(message.chat.id, f"Наши админы настолько ламповые, что круглосуточно восхищаются сами собой. Тебе не удалось поразить {message.reply_to_message.from_user.first_name}")

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
            await bot.send_message(message.chat.id, 'Вы недостаточно ламповы чтобы кого-то замутить :(')
            return

        if (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status == "restricted":
            await bot.send_message(message.chat.id, f'{message.reply_to_message.from_user.first_name} уже поражен и не может сказать ни слова.')

        else:
            dt_mute = datetime.timedelta(minutes=time_mute)
            await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=dt_mute)
            await bot.send_message(message.chat.id, f'{message.from_user.first_name} поразил своей ламповостью кота по имени {message.reply_to_message.from_user.first_name}.\n{message.reply_to_message.from_user.first_name} восхищен и не сможет сказать ни слова {dt_mute.seconds//60} мин. {dt_mute.seconds%60} сек.')
            user.amount -= int(time_mute)
            user.save()


