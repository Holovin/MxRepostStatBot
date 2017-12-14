import logging


class Config:
    # LOG
    LOG_FULL_PATH = 'log.txt'
    LOG_FORMAT = '%(module)-16s %(levelname)-8s [%(asctime)s] %(message)s'
    LOG_LEVEL = logging.INFO
    LOG_OUTPUT = True

    # OS
    TIMEZONE = 'Europe/Minsk'

    # DB
    SQLITE_DB_FULL_PATH = 'settings.db'

    # SETTINGS
    CHECK_SLEEP_TIME_SECONDS = 10

    WRITE_LIMIT_MINUTES_WHEN_NO_USERS = 240

    FEW_FROM = 1
    WRITE_LIMIT_MINUTES_WHEN_FEW_USERS = 120
    FEW_TO = 2

    WRITE_LIMIT_MINUTES_WHEN_MANY_USERS = 60

    LATEST_MC_LOG_FULL_PATH = 'latest.log'
    MC_SERVER_LINK = 'http://example.com'
    MC_SERVER_NAME = 'Test'

    TELEGRAM_PRINT_TO = '1'
    TELEGRAM_ADMIN_TO = '1'

    BOT_ID = '000000000'
    SECRET_TOKEN = 'ABCDEFGHIJKLMNOPQRSTVZXC123456'

    # JUST DON'T TOUCH
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:2.0b7) Gecko/20100101 Firefox/4.0b7'}

    MASTER_SETTINGS_ROW_ID = 0
