from peewee import *
import datetime
from settings import db


class BaseModel(Model):
    class Meta:
        database = db


class ChatModel(BaseModel):
    """Модель хранит уникальные чаты"""
    chat_id = IntegerField(unique=True)
    last_kalik = DateTimeField(default=(datetime.datetime.now() - datetime.timedelta(2)))

    class Meta:
        db_table = "models"


class UserModel(BaseModel):
    """Модель  хранит строки с уникальными парами user_id и chat """
    user_id = IntegerField()
    chat = ForeignKeyField(ChatModel, on_delete='CASCADE')
    amount = IntegerField(default=0)
    last_shava = DateTimeField(default=(datetime.datetime.now() - datetime.timedelta(2)))

    def save(self, force_insert=False, only=None):
        if self.amount < 0:
            self.amount = 0
        super().save()

    class Meta:
        db_table = "users"


def init():
    try:
        ChatModel.create_table()
    except InternalError as px:
        print(str(px))
    try:
        UserModel.create_table()
    except InternalError as px:
        print(str(px))


init()  # Создаем таблицы, если они еще не были созданы
