import datetime
import random
from asyncio import sleep
from contextlib import suppress

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lampa_bot.actions import get_hours_str, get_minutes_str
from models import ChatModel, UserModel


async def clear_messages(bot, message, sm, timeout=120, only_self=False):
    """ Принимает объект бота, объект входящего сообщения, объект исходящего сообщения, таймаут(сек).
    Удаляет отправленное ботом сообщение, и команду(либо сообщение) адресованное боту(при наличии прав админа)
    """
    await sleep(timeout)
    if not only_self:
        with suppress(Exception):
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    with suppress(Exception):
        await bot.delete_message(chat_id=sm.chat.id, message_id=sm.message_id)


class EatShawarmaStrategy:
    eating_now = {}

    def __init__(self, bot, message):
        self.bot = bot
        self.message = message
        self.user = self._get_user_from_message(message)

    async def start_eat_shawarma(self):
        print(self.user.last_shava)
        if datetime.datetime.now() < self.user.last_shava:
            await self._user_need_wait()
        elif f'{self.message.chat.id}_{self.message.from_user.id}' in self.eating_now:
            await self.shawarma_is_ready()
        else:
            await self.make_shawarma()

    async def _user_need_wait(self):
        time_to_next = self.user.last_shava - datetime.datetime.now()
        hours = time_to_next.seconds // 3600
        minutes = time_to_next.seconds % 3600 // 60
        texts = ['Ты недавно уже кушал(а), следующая шавуха будет через',
                 'Посмотри на свое пузо, хватит. Подожди еще хотя бы',
                 'Хватит жрать! Жди еще',
                 ]
        sm = await self.bot.send_message(self.message.chat.id,
                                         f'{random.choice(texts)} {hours} {get_hours_str(hours)} {minutes} {get_minutes_str(minutes)}',
                                         reply_to_message_id=self.message.message_id)
        await clear_messages(self.bot, self.message, sm)

    async def shawarma_is_ready(self):
        sm = await self.bot.send_message(self.message.chat.id, 'Ваша шавуха уже готова. Нажмите кнопку "Кушать"',
                                         reply_to_message_id=self.message.message_id)
        await clear_messages(self.bot, self.message, sm)

    async def make_shawarma(self):

        sm = await self.bot.send_message(self.message.chat.id, f'Шаурмастер аккуратно заворачивает вашу шавуху..',
                                         reply_markup=self._get_eat_kb(self.message),
                                         reply_to_message_id=self.message.message_id, )
        self.eating_now[f'{self.message.chat.id}_{self.message.from_user.id}'] = self
        await sleep(30)
        if f'{self.message.chat.id}_{self.message.from_user.id}' in self.eating_now:
            self.eating_now.pop(f'{self.message.chat.id}_{self.message.from_user.id}')
            await self.bot.edit_message_text(
                text=f'Шавуха остыла. {self.message.from_user.first_name} не успел её съесть, вместо этого наелся овсяной каши. +0 к ламповости',
                chat_id=sm.chat.id, message_id=sm.message_id,
                reply_markup='')
            await sleep(60)
        with suppress(Exception):
            await self.bot.delete_message(chat_id=self.message.chat.id, message_id=self.message.message_id)
        with suppress(Exception):
            await self.bot.delete_message(chat_id=sm.chat.id, message_id=sm.message_id)

    @staticmethod
    def _get_user_from_message(message):
        user, _ = UserModel.get_or_create(chat=ChatModel.get_or_create(chat_id=message.chat.id)[0],
                                          user_id=message.from_user.id)
        return user

    @staticmethod
    def _get_eat_kb(message):
        eat_kb = InlineKeyboardMarkup()
        eat_kb.add(InlineKeyboardButton('Кушать', callback_data=f'eating_now&{message.from_user.id}'))
        return eat_kb

    """ PART 2 """

    @classmethod
    async def eat_shawarma_call(cls, bot, call):
        if call.data.split('&')[1] != str(call.from_user.id):
            await call.answer(text="Эта шавуха не для тебя!")
        elif f'{call.message.chat.id}_{call.from_user.id}' not in cls.eating_now:
            await call.answer(text="Ты больше не можешь съесть эту шавуху")
        else:
            cls.eating_now.pop(f'{call.message.chat.id}_{call.from_user.id}')
            user = cls._get_user_from_message(call.message)
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
                await bot.send_message(call.message.chat.id,
                                       f'Кто-то выкинул шавуху кота по имени{call.from_user.first_name}')
            rh = random.randint(3, 6)
            user.last_shava = datetime.datetime.now() + datetime.timedelta(hours=rh)
            user.save()
            await call.answer(text="Приятного аппетита")
