import random
import datetime
from models import ChatModel, UserModel
from settings import TOKEN
from asyncio import sleep
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram import exceptions
from contextlib import suppress
muted_admins = []
eat_now = set()
smoke_chats = {}


async def clear_self(bot, message, sm, timeout=120):
    """ Принимает объект бота, объект входящего сообщения, объект исходящего сообщения, таймаут(сек).
    Удаляет отправленное ботом сообщение, и команду(либо сообщение) адресованное боту(при наличии прав админа)
    """
    await sleep(timeout)
    with suppress(Exception):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    with suppress(Exception):
        await bot.delete_message(chat_id=sm.chat.id, message_id=sm.message_id)


def get_hours_str(hours):
    """
    Принимает на ваход число -> (int)
    Возвращает слово "час" в нужном падеже -> (str)
    """
    if int(str(hours)[-1]) in [2, 3, 4] and hours not in [12, 13, 14]:
        hours_str = 'часа'
    elif int(str(hours)[-1]) == 1 and hours != 11:
        hours_str = 'час'
    else:
        hours_str = 'часов'
    return hours_str


def get_minutes_str(minutes, y=False):
    """
    Принимает число на ваход число -> (int) и параметр который заменяет (1)"минута" на (1)"минуту"
    Возвращает слово "минута" в нужном падеже -> (str)
    """
    if int(str(minutes)[-1]) in [2, 3, 4] and minutes not in [12, 13, 14]:
        minutes_str = 'минуты'
    elif int(str(minutes)[-1]) == 1 and minutes != 11:
        if y:
            minutes_str = 'минута'
        else:
            minutes_str = 'минуту'
    else:
        minutes_str = 'минут'
    return minutes_str


async def start(bot, message):
    start_text = "Добро пожаловать в лампового бота. Для старта добавьте меня в любой чат.\n Для подсказки по командам введите /help"
    await bot.send_message(message.from_user.id, start_text)


async def help(bot, message):
    help_text = "Бот позволяет копить ламповость кушая шаурму и куря кальян, и соревноватся с другими участниками чата в количестве имеющейся ламповости.\n /eat_shawarma - позволит вам получить  +5, +2 или -3 к ламповости\n /check_my_lampovost - просмотреть вашу ламповость в текущем чате \n /check_top_lampovyh_cats - просмотреть топ 20 человек в чате по количеству ламповости \n /smoke_kalik - собрать 5 человек за 5 минут. В случае удачи все получают +6 ламповости'\n\nПолученную ламповось можно потратить на мут других игроков. Для этого нужно в ответ на сообщение целевого пользователя отправить текст в формате \"мут <кол-во минут>\"\n\nДанные команды работают только в групповом чате, не пытайтесь их ввести здесь."
    await bot.send_message(message.from_user.id, help_text)


async def eat_shawarma(bot, message):
    """
    Игра в которой участник может получить +5, +2 или -3 к ламповости раз в 3-6 часов
    """
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    if datetime.datetime.now() < user.last_shava:
        time_to_next = user.last_shava - datetime.datetime.now()
        hours = time_to_next.seconds // 3600
        minutes = time_to_next.seconds % 3600 // 60
        texts = ['Ты недавно уже кушал(а), следующая шавуха будет через',
                 'Посмотри на свое пузо, хватит. Подожди еще хотя бы',
                 'Хватит жрать! Жди еще',
                 ]
        sm = await bot.send_message(message.chat.id, f'{random.choice(texts)} {hours} {get_hours_str(hours)} {minutes} {get_minutes_str(minutes)}', reply_to_message_id=message.message_id)
        await clear_self(bot, message, sm)
    else:
        if f'{message.chat.id}_{message.from_user.id}' in eat_now:
            sm = await bot.send_message(message.chat.id, 'Ваша шавуха уже готова. Нажмите кнопку "Кушать"',reply_to_message_id=message.message_id)
            await clear_self(bot, message, sm)
            return
        eat_mk = InlineKeyboardMarkup()
        eat_mk.add(InlineKeyboardButton('Кушать', callback_data=f'eat_now&{message.from_user.id}'))
        sm = await bot.send_message(message.chat.id, f'Шаурмастер аккуратно заворачивает вашу шавуху..', reply_markup=eat_mk, reply_to_message_id=message.message_id,)
        eat_now.add(f'{message.chat.id}_{message.from_user.id}')
        await sleep(30)
        if f'{message.chat.id}_{message.from_user.id}' in eat_now:
            eat_now.remove(f'{message.chat.id}_{message.from_user.id}')
            await bot.edit_message_text(text=f'Шавуха остыла. {message.from_user.first_name} не успел её съесть, вместо этого наелся овсяной каши. +0 к ламповости',
                                        chat_id=sm.chat.id, message_id=sm.message_id,
                                        reply_markup='')
            await sleep(60)
        with suppress(Exception):
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        with suppress(Exception):
            await bot.delete_message(chat_id=sm.chat.id, message_id=sm.message_id)

async def eat_shawarma_call(bot, call):
    if call.data.split('&')[1] != str(call.from_user.id):
        await call.answer(text="Эта шавуха не для тебя!")
    elif f'{call.message.chat.id}_{call.from_user.id}' not in eat_now:
        await call.answer(text="Ты больше не можешь съесть эту шавуху")
    else:
        eat_now.remove(f'{call.message.chat.id}_{call.from_user.id}')
        user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=call.message.chat.id)[0],
                                          user_id=call.from_user.id)
        try:
            if random.random() < 0.03:
                user.amount -= 15
                await bot.edit_message_text(text='Шаурма из г*вна. Всякое бывает. -15 к ламповости',
                                            chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            reply_markup='')
            else:
                r = random.randint(1, 3)
                if r == 1:
                    user.amount += 5
                    await bot.edit_message_text(text='Сладкая сочная шаурма. Пальчики оближешь. +5 к ламповости',
                                                chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup='')
                elif r == 2:
                    user.amount += 2
                    await bot.edit_message_text(text='Сносная шавуха. Ты утолил(а) свой голод. +2 к ламповости',
                                                chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup='')
                else:
                    user.amount += -3
                    await bot.edit_message_text(text='Придя домой ты знатно проблевался. -3 к ламповости',
                                                chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup='')
        except Exception:
            await bot.send_message(call.message.chat.id, f'Кто-то выкинул шавуху кота по имени{call.from_user.first_name}')
        rh = random.randint(3, 6)
        user.last_shava = datetime.datetime.now() + datetime.timedelta(hours=rh)
        user.save()
        await call.answer(text="Приятного аппетита")


async def check_my_lampovost(bot, message):
    """
    Выводит ламповость участника в текущем чате
    """
    texts = ['Шучу, не паникуй)0))', 'Повелся\U0001F602', 'А нет, я перепутал. Сори', 'Стоп. не то посмотрел', 'Тебя ограбили. Бывает']
    if random.random() < 0.02:
        sm1 = await bot.send_message(message.chat.id, f'Твоя ламповость:  0', reply_to_message_id=message.message_id)
        await sleep(8)
        sm2 = await bot.send_message(message.chat.id, random.choice(texts),)
        await sleep(3)
    user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                      user_id=message.from_user.id)
    sm = await bot.send_message(message.chat.id, f'Твоя ламповость:  {user.amount}', reply_to_message_id=message.message_id)
    await clear_self(bot, message, sm)


async def check_top_lampovyh_cats(bot, message):
    """
    Выводит топ 20 участников в текущем чате
    """
    chat, _ = ChatModel.get_or_create(chat_id=message.chat.id)
    text = 'Топ ламповых котов этого чата:\n\n'
    users = chat.usermodel_set.order_by(-UserModel.amount)
    counter = 1
    for i in users:
        if counter > 20:
            break
        with suppress(Exception):
            user_ = await bot.get_chat_member(message.chat.id, i.user_id)
            text += f"{counter}) {user_.user.first_name}:  {i.amount}\n"
            counter += 1
    await bot.send_message(message.chat.id, text)


async def mute_user(bot, message):
    """ При наличии прав администратора мутит пользователя указанного в message.reply_to_message.from_user.id на время подсчитанное по формуле sqrt(UserModel.amount)
    Если приходит запрос на мут адина, то вместо мута будут моментально удалятся все сообщения написанные админом указанное количество времени.
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

        elif (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status == "restricted" or f"{message.reply_to_message.from_user.id}_{message.chat.id}" in muted_admins:  # Если цель мута уже ограничена
            await bot.send_message(message.chat.id, f'{message.reply_to_message.from_user.first_name} уже поражен(а) и не может сказать ни слова.', reply_to_message_id=message.message_id)
        elif random.random() < 0.1:
            if (await bot.get_chat_member(message.chat.id, message.from_user.id)).status in ["administrator", "creator"]:  # Если целью мута является админ
                await bot.send_message(message.chat.id,
                                       f"Ха-ха, админ хотел замутить кота по имени {message.reply_to_message.from_user.first_name}, но замутил сам себя!\n{message.from_user.first_name} восхищен(а) и не сможет сказать ни слова {dt_mute.seconds // 60} мин. {dt_mute.seconds % 60} сек.",
                                       reply_to_message_id=message.message_id)
                muted_admins.append(f"{message.from_user.id}_{message.chat.id}")
                user.amount -= int(time_mute)
                user.save()
                await sleep(time_mute * 60)
                muted_admins.remove(f"{message.from_user.id}_{message.chat.id}")
            else:
                await bot.restrict_chat_member(message.chat.id, message.from_user.id,
                                               until_date=dt_mute)
                await bot.send_message(message.chat.id,
                                       f'{message.from_user.first_name} хотел поразить кота по имени {message.reply_to_message.from_user.first_name}, но {message.reply_to_message.from_user.first_name} схватил зеркало и отразил луч обратно!.\n{message.reply_to_message.first_name} восхищен(а) и не сможет сказать ни слова {dt_mute.seconds // 60} мин. {dt_mute.seconds % 60} сек.\nА вот не нужно быть таким злым!',
                                       reply_to_message_id=message.message_id)
                user.amount -= int(time_mute)
                user.save()

        elif (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status in ["administrator", "creator"]:  # Если целью мута является админ
            await bot.send_message(message.chat.id, f"Наши админы настолько ламповые, что круглосуточно восхищаются сами собой. Но всё-же тебе удалось поразить админа по имени {message.reply_to_message.from_user.first_name}.\n{message.reply_to_message.from_user.first_name} восхищен(а) и не сможет сказать ни слова {dt_mute.seconds//60} мин. {dt_mute.seconds%60} сек.", reply_to_message_id=message.message_id)
            muted_admins.append(f"{message.reply_to_message.from_user.id}_{message.chat.id}")
            user.amount -= int(time_mute)
            user.save()
            await sleep(time_mute * 60)
            muted_admins.remove(f"{message.reply_to_message.from_user.id}_{message.chat.id}")

        else:  # Если целью мута является обычный пользователь
            await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=dt_mute)
            await bot.send_message(message.chat.id, f'{message.from_user.first_name} поразил своей ламповостью кота по имени {message.reply_to_message.from_user.first_name}.\n{message.reply_to_message.from_user.first_name} восхищен(а) и не сможет сказать ни слова {dt_mute.seconds//60} мин. {dt_mute.seconds%60} сек.', reply_to_message_id=message.message_id)
            user.amount -= int(time_mute)
            user.save()


async def smoke_kalik(bot, message):
    """ Запускает процесс курения кальяна, в котором для получения ламповости необходимо набрать 5 человек за 5 минут.
    Выводит сообщение с оставшимся временем, уже присоеденившимся количеством участников и кнопкой для участия.
    """
    chat = ChatModel.get_or_create(chat_id=message.chat.id)[0]
    if message.chat.id in smoke_chats: # Если калик уже запущен
        sm = await bot.send_message(message.chat.id, f'<a href="https://t.me/c/{abs(message.chat.id+1_000_000_000_000)}/{smoke_chats[message.chat.id]["message_id"]}">Калик</a> уже заправлен, ждем пока соберется компания.', reply_to_message_id=message.message_id, parse_mode='HTML')
        await clear_self(bot, message, sm)
    elif datetime.datetime.now() - chat.last_kalik < datetime.timedelta(hours=5): # Если не прошло достаточно времени с прошлого курения в данном чате
        time_to_next = datetime.timedelta(hours=5) - (datetime.datetime.now() - chat.last_kalik)
        hours = time_to_next.seconds // 3600
        minutes = time_to_next.seconds % 3600 // 60
        sm = await bot.send_message(message.chat.id, f'Во время последнего посещения кальянной вас застукали менты и прикрыли заведение за нарушение правил локдауна. Подождите пока все уляжется. Ждать осталось {hours} {get_hours_str(hours)} {minutes} {get_minutes_str(minutes)}', reply_to_message_id=message.message_id)
        await clear_self(bot, message, sm)
    else:  # если все ок
        smoke_chats[message.chat.id] = {'users': []}  # создаем событие курения в чате, и список юзеров
        smoke_chats[message.chat.id]['users'].append(message.from_user.id)  # добавляем юзера который инициировал калик
        inline_btn = InlineKeyboardMarkup().add(InlineKeyboardButton('Присоединится', callback_data='join_kalik'))  # Кнопка для остальных участников
        message_info = await bot.send_message(message.chat.id, f"До конца сборов 5 минут, ждем 5 человек. Статус: {len(smoke_chats[message.chat.id]['users'])}/5", reply_markup=inline_btn)
        smoke_chats[message.chat.id]["message_id"] = message_info.message_id  # Сохраняем id сообщения с кнопкой
        smoke_chats[message.chat.id]["timeout"] = 5  # Устанавливаем таймаут
        for i in range(smoke_chats[message.chat.id]["timeout"]):
            smoke_chats[message.chat.id]["timeout"] -= 1
            await sleep(60)
            if message.chat.id not in smoke_chats:
                with suppress(Exception):
                    await bot.delete_message(chat_id=message_info.chat.id, message_id=message_info.message_id)
                return
            with suppress(Exception):
                await bot.edit_message_text(chat_id=message_info.chat.id, message_id=message_info.message_id, text=f"До конца сборов {smoke_chats[message.chat.id]['timeout']} {get_minutes_str(smoke_chats[message.chat.id]['timeout'], y=True)}, ждем 5 человек. Статус: {len(smoke_chats[message.chat.id]['users'])}/5", reply_markup=inline_btn)
        with suppress(Exception):
            await bot.delete_message(chat_id=message_info.chat.id, message_id=message_info.message_id)
        del smoke_chats[message.chat.id]
        await bot.send_message(message.chat.id, "Пока вы ждали прибыла полиция, которая не пускает новых посетителей из-за нарушения режима локдауна. Вы не успели проскочить внутрь :(")
        chat.last_kalik = datetime.datetime.now() - datetime.timedelta(hours=2.5)
        chat.save()


async def join_to_kalik(bot, call):
    """ Неразрывно связанная с функцией smoke_kalik(), срабатывает при нажатии кнопки.
    После того как будет набрано нужное количество людей, всем участникам будет выдано +6 к ламповости.
    """
    if call.message.chat.id in smoke_chats:
        if call.from_user.id in smoke_chats[call.message.chat.id]['users']:
            await call.answer(text="Вы уже присоеденились к компании. Ждите остальных")
        else:
            smoke_chats[call.message.chat.id]['users'].append(call.from_user.id)
            inline_btn = InlineKeyboardMarkup().add(InlineKeyboardButton('Присоединится', callback_data='join_kalik'))
            with suppress(Exception):
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=smoke_chats[call.message.chat.id]["message_id"], text=f"До конца сборов {smoke_chats[call.message.chat.id]['timeout']+1} {get_minutes_str(smoke_chats[call.message.chat.id]['timeout']+1, y=True)}, ждем 5 человек. Статус: {len(smoke_chats[call.message.chat.id]['users'])}/5",reply_markup=inline_btn)
            await call.answer(text="Вы успешно присоеденились к компании")
            if len(smoke_chats[call.message.chat.id]['users']) >= 5:
                with suppress(exceptions.MessageCantBeDeleted):
                    await bot.delete_message(chat_id=call.message.chat.id, message_id=smoke_chats[call.message.chat.id]["message_id"])
                text = "Ламповые коты "
                for i in smoke_chats[call.message.chat.id]['users']:
                    user = UserModel.get_or_create(user_id=i, chat=ChatModel.get_or_create(chat_id=call.message.chat.id)[0])[0]
                    user_ = await bot.get_chat_member(call.message.chat.id, i)
                    if random.random() < 0.1:
                        user.amount -= 12
                        user.save()
                        await bot.send_message(call.message.chat.id, f'{user_.user.first_name} словил бледного и получил -12 к ламповости')
                        await sleep(2)
                        continue
                    if i == smoke_chats[call.message.chat.id]['users'][-1]:
                        text = text[:-2]
                        text += f" и <a href='https://t.me/{user_.user.username}'>{user_.user.first_name}</a> "
                    else:
                        text += f"<a href='https://t.me/{user_.user.username}'>{user_.user.first_name}</a>, "
                    user.amount += 6
                    user.save()
                text += "C кайфом покурили калик и получили + 6 к ламповости!"
                await bot.send_message(call.message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)
                chat = ChatModel.get_or_create(chat_id=call.message.chat.id)[0]
                chat.last_kalik = datetime.datetime.now()
                chat.save()
                del smoke_chats[call.message.chat.id]
