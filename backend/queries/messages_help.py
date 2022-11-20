from ..database import SubjectsTable, MessagesTable, Message
from datetime import datetime
from ..config import Config
import telebot
import os


def send_message_to_telegram(title, content, year):
    bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
    msg = '<b>' + title + '</b>\n' + content
    msg = msg.replace('href="', 'href="{}{}/'.format(Config.HOST, year))
    bot.send_message(os.getenv('TELEGRAM_CHAT'), msg, parse_mode='html')


def message_results_public(year, subject):
    subject = SubjectsTable.select(subject)
    title = subject.name
    was_old = len(MessagesTable.select_by_year_and_title(year, title))
    content = 'Опубликованы' if not was_old else 'Обновлены'
    content += ' <a href="{}.html">результаты {}.</a>'.format(subject.id, subject.msg)
    MessagesTable.insert(Message([None, year, title, content, int(datetime.now().timestamp())]))
    send_message_to_telegram(title, content, year)


def message_timetable_public(year):
    title = 'Расписание'
    was_old = len(MessagesTable.select_by_year_and_title(year, title))
    content = 'Опубликовано' if not was_old else 'Обновлено'
    content += ' <a href="timetable.html">расписание ИТИ.</a>'
    MessagesTable.insert(Message([None, year, title, content, int(datetime.now().timestamp())]))
    send_message_to_telegram(title, content, year)


def message_ratings_public(year):
    title = 'Рейтинг'
    was_old = len(MessagesTable.select_by_year_and_title(year, title))
    content = 'Опубликован' if not was_old else 'Обновлен'
    content += ' <a href="rating.html">рейтинг ИТИ.</a>'
    MessagesTable.insert(Message([None, year, title, content, int(datetime.now().timestamp())]))
    send_message_to_telegram(title, content, year)


def message_all_ratings_public(year, subjects):
    title = 'Текущие результаты'
    content = 'На данный момент все результаты на сайте соответствуют результатам проверки работ.\n<ul>\n'
    content += '<li><a href="rating.html">Рейтинги</a></li>\n'
    for subject in subjects:
        content += '<li><a href="{}.html">{}</a></li>\n'.format(subject.id, subject.name)
    content += '</ul>\n'
    MessagesTable.insert(Message([None, year, title, content, int(datetime.now().timestamp())]))
    send_message_to_telegram(title, content, year)


def message_teams_public(year):
    title = 'Команды'
    content = 'Все команды ИТИ целиком сформированы, <a href="teams.html">списки команд.</a>'
    MessagesTable.insert(Message([None, year, title, content, int(datetime.now().timestamp())]))
    send_message_to_telegram(title, content, year)
