import pytz
from peewee import *
from datetime import datetime

from config import Config
from helpers.db_connect import Database


class BaseModel(Model):
    class Meta:
        database = Database.get_db()


class User(BaseModel):
    id = PrimaryKeyField(primary_key=True)

    # user minecraft name
    name = CharField(null=False)

    # 1st event time with this user (aka register time)
    time_registration = DateTimeField(null=False, default=datetime.now)

    # how many times user had logged in
    total_enter_times = IntegerField(null=False, default=0)

    # last enter event
    time_last_login = DateTimeField(null=False)

    # last logout event
    time_last_logout = DateTimeField(null=False)

    # total online time in seconds
    time_online_total = IntegerField(null=False)

    # day online time in seconds
    time_online_day = IntegerField(null=False)


class BotData(BaseModel):
    id = PrimaryKeyField(primary_key=True)

    # last check
    time_last_check = DateTimeField(null=False, default=datetime.now(pytz.timezone(Config.TIMEZONE)))

    # last write
    time_last_write = DateTimeField(null=False, default=datetime.now(pytz.timezone(Config.TIMEZONE)))

    # write every [...] if no events
    time_write_every = IntegerField(null=False, default=Config.WRITE_LIMIT_MINUTES_WHEN_NO_USERS)

    # total for count +[...]
    total_all_users = IntegerField(null=False, default=0)

    # yesterday total day
    total_yesterday_users = IntegerField(null=False, default=0)

    # online before last check
    total_online_previous = IntegerField(null=False, default=0)
