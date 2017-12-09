# UxMineBot
Collect and send minecraft server stats from mc log file to telegram user/chat.

## Installation
1. Clone repo
1. Install dependencies from requirements.txt (like pip install or with your virtualenv/conda environment)
1. Run python3 main.py (or write .sh script for your needs)

## Config
### Important
- `LATEST_MC_LOG_FULL_PATH` - path to minecraft sever log (like `.../server/logs/latest.log`)
- `MC_SERVER_LINK` - link to server in bot message
- `MC_SERVER_NAME` - link text in bot message
- `CHECK_SLEEP_TIME_SECONDS` - check period (every X seconds, best choice value `60`)

Bot writing every X minutes even when no 'important' events (new user, new day):
- `WRITE_LIMIT_MINUTES_WHEN_NO_USERS` - write every X minutes when 0 users (default: 240)
- `WRITE_LIMIT_MINUTES_WHEN_FEW_USERS` - write every X minutes when 1..2 users (default: 60)
- `WRITE_LIMIT_MINUTES_WHEN_MANY_USERS` - write every X minutes when 3+ users (default: 20)

### System vars
- `LOG_FULL_PATH` - path to app logfile (like `LOG_FULL_PATH = 'log.txt'`)
- `LOG_FORMAT` - default python logger format string
- `LOG_LEVEL` - min level to log
- `LOG_OUTPUT` - `True` value allow duplicate log output to console

### OS
- `TIMEZONE` - timezone for logfile and check timers

### DB
DB will be created when db file not found (usually 1st run time)
For database config see table structure in `helpers/db_models.py` file.
- `SQLITE_DB_FULL_PATH` - path to sqlite db

### Telegram
- `TELEGRAM_PRINT_TO` - chat id for receive 'main' log
- `TELEGRAM_ADMIN_TO` - chat id for admin logs (exceptions and other what you need)

- `BOT_ID` - telegram bot id (numbers before semicolon in 123456:abce123fgbji...)
- `SECRET_TOKEN` - telegram bot token (text after semicolon 123456:abce123fgbji...)

### Other (just don't touch)
- `HEADERS` - headers for HTTPS requests
- `MASTER_SETTINGS_ROW_ID` - record id for master row in settings db

## Changelog
### v0.0-r3 - 10.12.2017
Day stats count

### v0.0-r2 - 09.12.2017
First 'stable' alpha

### v0.0-r1 - 07.12.2017
Forked from D_UxRepostStatBot
