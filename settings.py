import peewee

try:
    # Импорт локальных настроек
    from local_settings import *

except ImportError:
    # Заменить токен на токен бота
    TOKEN = "954054488:AAE10YWU4kWtgZJht3Fyansy1vxiQqXoUgk"
    # При необходимости заменить sqlite на другую базу данных
    db = peewee.SqliteDatabase('data.db')
