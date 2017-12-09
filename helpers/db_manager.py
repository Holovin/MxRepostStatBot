from config import Config
from helpers import db_models
from helpers.db_models import BotData


class Serve:
    @staticmethod
    def create_tables(db):
        db.connect()
        db.create_tables([db_models.User, db_models.BotData])

        bot_data = BotData.create(id=Config.MASTER_SETTINGS_ROW_ID)
        bot_data.save()

    @staticmethod
    def drop_tables(db):
        db.connect()
        db.drop_tables([db_models.User, db_models.BotData])
