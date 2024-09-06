import os
import re
import telebot

from ..config import Config
from ..database import Message, Subject
from ..help import get_timestamp


def send_message_to_telegram(title, content, year):
    bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
    msg = '<b>' + title + '</b>\n' + content
    msg = re.sub(r"<!--.*-->", "", msg)
    msg = msg.replace('href="', 'href="{}{}/'.format(Config.HOST, year))
    msg = msg.replace('<ul>', '').replace('</ul>', '').replace('<li>', '\n● ').replace('</li>', '')
    msg = msg.replace('<br>', '\n')
    bot.send_message(os.getenv('TELEGRAM_CHAT'), msg, parse_mode='html')


def message_save(title, content, year, priority=0):
    Message.insert(Message.build(None, year, title, content, get_timestamp(), priority))
    send_message_to_telegram(title, content, year)


def message_results_public(year, subject):
    subject = Subject.select(subject)
    title = subject.name
    was_old = len(Message.select_by_iti_and_title(year, title))
    content = 'Опубликованы' if not was_old else 'Обновлены'
    content += ' <a href="{}">результаты {}.</a>'.format(subject.id, subject.msg)
    message_save(title, content, year)


def message_timetable_public(year):
    title = 'Расписание'
    was_old = len(Message.select_by_iti_and_title(year, title))
    content = 'Опубликовано' if not was_old else 'Обновлено'
    content += ' <a href="timetable">расписание ИТИ.</a>'
    message_save(title, content, year)


def message_ratings_public(year):
    title = 'Рейтинги'
    was_old = len(Message.select_by_iti_and_title(year, title))
    content = 'Опубликованы' if not was_old else 'Обновлены'
    content += ' рейтинги ИТИ:<ul>'\
               '<li><a href="rating_students">Рейтинг школьников</a></li>' \
               '<li><a href="rating_classes">Рейтинг классов</a></li>' \
               '<li><a href="rating_teams">Рейтинг команд</a></li>' \
               '<li><a href="rating">Все рейтинги</a></li></ul>'
    message_save(title, content, year)


def message_all_ratings_public(year, subjects):
    title = 'Текущие результаты'
    content = 'На данный момент все результаты на сайте соответствуют результатам проверки работ.\n<ul>\n'
    content += '<li><a href="rating">Рейтинги</a></li>\n'
    for subject in subjects:
        content += '<li><a href="{}">{}</a></li>\n'.format(subject.id, subject.name)
    content += '</ul>\n'
    message_save(title, content, year)


def message_teams_public(year):
    title = 'Команды'
    content = 'Все команды ИТИ целиком сформированы, <a href="rating_teams">списки и рейтинги команд.</a>'
    message_save(title, content, year)
