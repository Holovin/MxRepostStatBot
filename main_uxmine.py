#!/usr/bin/python3

import logging
import time
import os
import re
import traceback

from dateutil.parser import parse
from pytz import timezone
from datetime import datetime, timedelta

from config import Config
from api import API
from helpers.db_connect import Database
from helpers.db_manager import Serve
from helpers.db_models import User, BotData
from helpers.logger import logger_setup


LOGGER_NAME = 'ux_mine_bot'

MARKDOWN_ESCAPE = str.maketrans({
    '\\': r'\\',
    '*': r'\*',
    '_': r'\_',
    '[': r'\[',
    '(': r'\(',
    '`': r'\`'
})


class Events:
    new_users = False
    new_day = False
    new_test = False


def str_to_time(data):
    if type(data) is str:
        return parse(data)

    return data


def markdown_escape(text):
    return text.translate(MARKDOWN_ESCAPE)


def get_medal(place):
    if place == 1:
        return '\U0001F947'

    if place == 2:
        return '\U0001F948'

    if place == 3:
        return '\U0001F949'

    return '{}. '.format(place)


if __name__ == '__main__':
    # logs
    logger = logging.getLogger(LOGGER_NAME)
    logger_setup(Config.LOG_FULL_PATH, [LOGGER_NAME], True)

    # init
    app = API(Config.BOT_ID, Config.SECRET_TOKEN, logger)
    tz = timezone(Config.TIMEZONE)

    # 1st run
    if not os.path.isfile(Config.SQLITE_DB_FULL_PATH):
        Serve.create_tables(Database.get_db())
        app.api_send_message(Config.TELEGRAM_ADMIN_TO, 'Bot init ok!')
        logger.info('Tables created. Need restart...')
        exit(100)

    # db
    database = Database.get_db()
    database.connect()

    # map db to memory
    users = []

    # read db #1
    for user in User.select():
        users.append(user)

    # read db #2
    bot_data = BotData.get(BotData.id == Config.MASTER_SETTINGS_ROW_ID)

    # check log_lines file
    if not os.path.isfile(Config.LATEST_MC_LOG_FULL_PATH):
        logger.fatal('Can''t find log file from minecraft')
        database.close()
        exit(101)

    # (c) Блеать как ты так пишешь экспрешены
    # precompile rexgex
    re_log_line = re.compile('^\[(?P<time_h>\d{2}):(?P<time_m>\d{2}):(?P<time_s>\d{2})\].+: (?P<name>.*?)(\[\/.+\])? (?P<event_type>left|logged).+$')
    logger.info('Init ok...')

    # __ DO
    while True:
        try:
            logger.info('Start [last check was at {}, last write was at {}]'.format(bot_data.time_last_check, bot_data.time_last_write))

            # init loop
            Events.new_users = False
            Events.new_day = True
            Events.new_test = False

            log_lines = None
            time_iteration_start = datetime.now(tz)

            # freeze time
            if time_iteration_start.day != str_to_time(bot_data.time_last_check).day or time_iteration_start.day != str_to_time(bot_data.time_last_write).day:
                logging.info('Sleep for long time (new day)')
                time.sleep(Config.CHECK_NEW_DAY_DELAY_SECONDS)
                Events.new_day = True

            # need check?
            elif time_iteration_start - str_to_time(bot_data.time_last_check) < timedelta(seconds=Config.CHECK_SLEEP_TIME_SECONDS):
                logger.info('Sleep for {} seconds'.format(Config.CHECK_SLEEP_TIME_SECONDS))
                bot_data.time_last_check = datetime.now(tz)
                bot_data.save()
                time.sleep(Config.CHECK_SLEEP_TIME_SECONDS)
                continue

            # update
            bot_data.time_last_check = datetime.now(tz)
            bot_data.save()

            # start check
            with open(Config.LATEST_MC_LOG_FULL_PATH, 'r', encoding='utf-8') as log_file:
                log_lines = log_file.readlines()

            # check file
            if not log_lines:
                logger.warning('No log lines! Seems empty file?')
                continue

            # parse events
            for log_event_line in log_lines:
                event = re_log_line.match(log_event_line.replace('{}[m'.format(chr(27)), ''))

                # skip wrong line
                if not event:
                    continue

                # skip if someone so smart and try make injection
                if 'issued server command:' in log_event_line:
                    logger.warning('Skip injection line')
                    continue

                # unpack
                event = event.groupdict()

                # convert time
                event_time = time_iteration_start.replace(
                    hour=int(event.get('time_h')),
                    minute=int(event.get('time_m')),
                    second=int(event.get('time_s')),
                    microsecond=0
                )

                # skip old lines
                if str_to_time(bot_data.time_last_read) >= event_time:
                    logger.info('Skip line: {}'.format(log_event_line[:80]))
                    continue

                bot_data.time_last_read = event_time

                # debug
                logger.debug('Parsed {} :: {} {}'.format(event_time, event.get('name'), event.get('event_type')))

                # find user
                user = next((x for x in users if x.name == event.get('name')), None)

                # not found => add new user
                if not user:
                    Events.new_users = True
                    user = User.create(
                        name=event.get('name'),
                        time_registration=event_time,
                        total_enter_times=0,
                        time_last_login=event_time,
                        time_last_logout=event_time - timedelta(seconds=1),
                        time_online_total=0,
                        time_online_day=0,
                    )

                    # update memory db
                    users.append(user)

                logger.info('Use user {}'.format(user.name))

                # parse log_lines-in event
                if event.get('event_type') == 'logged':
                    user.time_last_login = event_time
                    user.total_enter_times += 1

                    msg = '*[Admin]* ({:%Y/%m/%d %H:%M:%S})\nЮзер {} _зашёл_ ({})\n' \
                        .format(event_time, markdown_escape(user.name), user.total_enter_times)

                    logger.debug(msg)
                    app.api_send_message(Config.TELEGRAM_ADMIN_TO, msg, 'markdown')

                # parse log_lines-out event
                elif event.get('event_type') == 'left':
                    user.time_last_logout = event_time
                    user.time_last_login = str_to_time(user.time_last_login)

                    # if user login and logout at same day
                    if user.time_last_logout.date() == user.time_last_login.date():
                        last_session_duration = (user.time_last_logout - user.time_last_login).seconds
                    else:
                        # if not count difference from current day with [logout - 00:00:00.0000] time
                        last_session_duration = (user.time_last_logout - user.time_last_logout.replace(hour=0, minute=0, second=0, microsecond=0)).seconds

                    user.time_online_day += last_session_duration
                    user.time_online_total += last_session_duration

                    msg = '*[Admin]* ({:%Y/%m/%d %H:%M:%S})\nЮзер {} _вышел_ ({})\nСессия (мин): {}\n' \
                        .format(event_time, markdown_escape(user.name), user.total_enter_times, last_session_duration // 60)

                    logger.debug(msg)
                    app.api_send_message(Config.TELEGRAM_ADMIN_TO, msg, 'markdown')

                # save anyway
                user.save()

            # recount daily time stat if new day
            if Events.new_day:
                for user in users:
                    if user.time_last_login > user.time_last_logout:
                        # count difference from login time and "current" time [~00:00:00.0000] of new day
                        last_session_duration = (bot_data.time_last_check - str_to_time(user.time_last_login)).seconds

                        user.time_online_day += last_session_duration
                        user.time_online_total += last_session_duration

                        # save only if update online time
                        user.save()

            # update
            message = ''
            trigger_message = ''
            seconds_from_previous_message = datetime.now(tz) - str_to_time(bot_data.time_last_write)

            total_all_users = User.select().count()
            total_new_users = User.select().where(User.time_registration > bot_data.time_last_write)
            total_today_users = User.select().where(User.time_last_login > datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)).count()
            total_online_users = User.select().where(User.time_last_login > User.time_last_logout).count()

            bot_data.time_last_write = datetime.now(tz)

            # change limits
            if total_online_users == 0:
                bot_data.time_write_every = Config.WRITE_LIMIT_MINUTES_WHEN_NO_USERS

            elif Config.FEW_FROM <= total_online_users <= Config.FEW_TO:
                bot_data.time_write_every = Config.WRITE_LIMIT_MINUTES_WHEN_FEW_USERS

            else:
                bot_data.time_write_every = Config.WRITE_LIMIT_MINUTES_WHEN_MANY_USERS

            # check triggers
            if Events.new_test:
                trigger_message = '[DEBUG MODE]'

            # 1 -- new user
            elif Events.new_users:
                # append
                trigger_message = 'Новые пользователи: '

                for new_user in total_new_users:
                    trigger_message += '{}, '.format(markdown_escape(new_user.name))

                # fix last char
                trigger_message = trigger_message.strip(', ')

            # 2 -- new day
            elif Events.new_day:
                trigger_message = '\n*Игроки дня:*'

                for i, user in enumerate(User.select().where(User.time_online_day > 0).order_by(User.time_online_total.desc()).limit(Config.DAY_REPORT_USERS_TOP_LIMIT)):
                    trigger_message += '\n{}{}: {} ({})'.format(get_medal(i + 1), markdown_escape(user.name), user.time_online_day // 60, user.time_online_total // 60)

                # reset cache
                # for user in users:
                #     print(user.time_online_day)
                #     user.time_online_day = 0
                #     print('new {}'.format(user.time_online_day))
                #     user.save()

            # check
            elif seconds_from_previous_message < timedelta(seconds=bot_data.time_write_every * 60) and not trigger_message:
                logger.info('Skip writing, because timedelta is low + no important events')
                continue

            # 3 -- no trigger - check timer
            else:
                trigger_message = ''

            # prepare report
            message = ('*MX Stats:* [{}]({}) ({:%Y/%m/%d %H:%M:%S})\n'
                       'Всего игроков: {:d} ({:+d})\n'
                       'Сегодня играло: {:+d} ({:+d})\n'
                       'Онлайн: {:+d} ({:+d})\n'
                       '{}\n'
                       '#uxmine'
                       .format(Config.MC_SERVER_NAME, Config.MC_SERVER_LINK, bot_data.time_last_write,
                               total_all_users, (total_all_users - bot_data.total_all_users),
                               total_today_users, (total_today_users - bot_data.total_yesterday_users),
                               total_online_users, (total_online_users - bot_data.total_online_previous),
                               trigger_message))

            app.api_send_message(Config.TELEGRAM_PRINT_TO, message, 'markdown')

            if Config.TELEGRAM_PRINT_TO != Config.TELEGRAM_ADMIN_TO:
                app.api_send_message(Config.TELEGRAM_ADMIN_TO, message, 'markdown')

            logging.info('Send message... {}'.format(message))

            # update
            bot_data.total_all_users = total_all_users
            bot_data.total_online_previous = total_online_users

            if Events.new_day:
                # reset user data [after write event about this]
                User.update(time_online_day=0).execute()
                bot_data.total_yesterday_users = total_today_users

            bot_data.save()

        except Exception as e:
            message = '\U0001F914 Exception: {}\nTraceback: {}'.format(e, traceback.format_exc())
            logger.error(message)
            app.api_send_message(Config.TELEGRAM_ADMIN_TO, '_[ERROR]:_\n```{}```'.format(message), 'markdown')
            time.sleep(Config.CHECK_SLEEP_TIME_SECONDS * 2)

        finally:
            logger.info('End iteration...\n---')
