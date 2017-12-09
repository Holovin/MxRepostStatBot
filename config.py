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
    WRITE_LIMIT_MINUTES_WHEN_FEW_USERS = 60
    WRITE_LIMIT_MINUTES_WHEN_MANY_USERS = 20

    LATEST_MC_LOG_FULL_PATH = 'server/logs/latest.log'  # <-- you need change this
    MC_SERVER_LINK = 'http://'                          # <-- you need change this
    MC_SERVER_NAME = 'Server'                           # <-- you need change this

    TELEGRAM_PRINT_TO = '000000'                        # <-- you need change this
    TELEGRAM_ADMIN_TO = '000000'                        # <-- you need change this

    BOT_ID = '000000000'                                # <-- you need change this
    SECRET_TOKEN = 'ABCDEFGHIJKLMNOPQRSTVZXC123456'     # <-- you need change this

    # JUST DON'T TOUCH
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:2.0b7) Gecko/20100101 Firefox/4.0b7'}

    MASTER_SETTINGS_ROW_ID = 0
