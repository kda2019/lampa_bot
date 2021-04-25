import peewee

try:
    # Импорт локальных настроек
    from local_settings import *

except ImportError:
    # Заменить токен на токен бота
    TOKEN = "token"
    # При необходимости заменить sqlite на другую базу данных
    db = peewee.SqliteDatabase('data.db')
