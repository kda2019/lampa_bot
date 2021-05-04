import random, datetime
from models import ChatModel, UserModel
from settings import TOKEN
from asyncio import sleep
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import exceptions
data = []
smoke_chats = {}


def get_hours_str(hours):
    if hours in [2, 3, 4]:
        hours_str = 'часа'
    elif hours == 1:
        hours_str = 'час'
    else:
        hours_str = 'часов'
    return hours_str


def get_minutes_str(minutes, now=False):
    if minutes in [2, 3, 4]:
        minutes_str = 'минуты'
    elif minutes == 1:
        if now:
            minutes_str = 'минута'
        else:
            minutes_str = 'минуту'
    else:
        minutes_str = 'минут'
    return minutes_str


async def start(bot, message):
    start_text = "Добро пожаловать в лампового бота. Для старта добавьте меня в любой чат.\ Для подсказки по командам введите /help"
    await bot.send_message(message.from_user.id, start_text)


async def help(bot, message):
    help_text = "Бот позволяет копить ламповость кушая шаурму и куря кальян, и соревноватся с другими участниками чата в количестве имеющейся ламповости.\n /eat_shawarma - позволит вам получить  +5, +2 или -3 к ламповости\n /check_my_lampovost - просмотреть вашу ламповость в текущем чате \n /check_top_lampovyh_cats - просмотреть топ 20 человек в чате по количеству ламповости\n\nДанные команды работают только в групповом чате, не пытайтесь их ввести здесь."
    await bot.send_message(message.from_user.id, help_text)


async def eat_shawarma(bot, message):
    """
    Игра в которой юзер может получить +5, +2 или -3 к ламповости раз в 4 часа
    """
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    if datetime.datetime.now() - user.last_shava < datetime.timedelta(hours=4):
        time_to_next = datetime.timedelta(hours=4) - (datetime.datetime.now() - user.last_shava)
        hours = time_to_next.seconds // 3600
        minutes = time_to_next.seconds % 3600 // 60
        await bot.send_message(message.chat.id, f'Ты недавно уже кушал(а), сдедующая шавуха будет через {hours} {get_hours_str(hours)} {minutes} {get_minutes_str(minutes)}', reply_to_message_id=message.message_id)
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
    """
    Выводит ламповость юзера в текущем чате
    """
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    await bot.send_message(message.chat.id, f'Твоя ламповость:  {user.amount}', reply_to_message_id=message.message_id)


async def check_top_lampovyh_cats(bot, message):
    """
    Выводит топ 20 юзеров в текущем чате
    """
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
                await bot.send_message(message.chat.id, 'Время мута не должно быть меньше 1 минуты', reply_to_message_id=message.message_id)
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


async def smoke_kalik(bot, message):
    chat = ChatModel.get_or_create(chat_id=message.chat.id)[0]
    if message.chat.id in smoke_chats:
        await bot.send_message(message.chat.id, f'<a href="https://t.me/c/{abs(message.chat.id+1_000_000_000_000)}/{smoke_chats[message.chat.id]["message_id"]}">Калик</a> уже заправлен, ждем пока соберется компания.', reply_to_message_id=message.message_id, parse_mode='HTML')
    elif datetime.datetime.now() - chat.last_kalik < datetime.timedelta(hours=5):
        time_to_next = datetime.timedelta(hours=5) - (datetime.datetime.now() - chat.last_kalik)
        hours = time_to_next.seconds // 3600
        minutes = time_to_next.seconds % 3600 // 60
        await bot.send_message(message.chat.id, f'Во время последнего посещения кальянной вас застукали менты и прикрыли заведение за нарушение правил локдауна. Подождите пока все уляжется. Ждать осталось {hours} {get_hours_str(hours)} {minutes} {get_minutes_str(minutes)}', reply_to_message_id=message.message_id)
    else:
        smoke_chats[message.chat.id] = {'users': []}
        smoke_chats[message.chat.id]['users'].append(message.from_user.id)
        inline_btn = InlineKeyboardMarkup().add(InlineKeyboardButton('Присоединится', callback_data='join_kalik'))
        message_info = await bot.send_message(message.chat.id, f"До конца сборов 5 минут, ждем 5 человек. Статус: {len(smoke_chats[message.chat.id]['users'])}/5", reply_markup=inline_btn)
        smoke_chats[message.chat.id]["message_id"] = message_info.message_id
        smoke_chats[message.chat.id]["timeout"] = 5
        for i in range(smoke_chats[message.chat.id]["timeout"]):
            smoke_chats[message.chat.id]["timeout"] -= 1
            await sleep(60)
            if message.chat.id not in smoke_chats:
                await bot.delete_message(chat_id=message_info.chat.id, message_id=message_info.message_id)
                return
            try:
                await bot.edit_message_text(chat_id=message_info.chat.id, message_id=message_info.message_id, text=f"До конца сборов {smoke_chats[message.chat.id]['timeout']} {get_minutes_str(smoke_chats[message.chat.id]['timeout'], now=True)}, ждем 5 человек. Статус: {len(smoke_chats[message.chat.id]['users'])}/5", reply_markup=inline_btn)
            except exceptions.MessageNotModified:
                pass
        await bot.delete_message(chat_id=message_info.chat.id, message_id=message_info.message_id)
        print(smoke_chats[message.chat.id])
        del smoke_chats[message.chat.id]
        await bot.send_message(message.chat.id, "Пока вы ждали прибыла полиция, которая не пускает новых посетителей из-за нарушения режима локдауна. Вы не успели проскочить внутрь :(")
        chat.last_kalik = datetime.datetime.now() - datetime.timedelta(hours=2.5)
        chat.save()


async def join_to_kalik(bot, call):
    if call.from_user.id in smoke_chats[call.message.chat.id]['users']:
        await call.answer(text="Вы уже присоеденились к компании. Ждите остальных")
    else:
        smoke_chats[call.message.chat.id]['users'].append(call.from_user.id)
        inline_btn = InlineKeyboardMarkup().add(InlineKeyboardButton('Присоединится', callback_data='join_kalik'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=smoke_chats[call.message.chat.id]["message_id"], text=f"До конца сборов {smoke_chats[call.message.chat.id]['timeout']+1} {get_minutes_str(smoke_chats[call.message.chat.id]['timeout']+1, now=True)}, ждем 5 человек. Статус: {len(smoke_chats[call.message.chat.id]['users'])}/5",reply_markup=inline_btn)
        await call.answer(text="Вы успешно присоеденились к компании")
        if len(smoke_chats[call.message.chat.id]['users']) >= 5:
            text = "Ламповые коты "
            for i in smoke_chats[call.message.chat.id]['users']:
                user = UserModel.get_or_create(user_id=call.from_user.id)[0]

                user_ = await bot.get_chat_member(call.message.chat.id, i)
                if i == smoke_chats[call.message.chat.id]['users'][-1]:
                    text = text[:-2]
                    text += f" и <a href='https://t.me/{user_.user.username}'>{user_.user.first_name}</a> "
                else:
                    text += f"<a href='https://t.me/{user_.user.username}'>{user_.user.first_name}</a>, "
                user.amount += 6
                user.save()
            await bot.delete_message(chat_id=call.message.chat.id, message_id=smoke_chats[call.message.chat.id]["message_id"])
            text += "с кайфом покурили калик и получили + 6 к ламповости!"
            await bot.send_message(call.message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)
