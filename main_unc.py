# -*- coding: utf-8 -*-

import collections
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from requests import get
import pymysql
import sys


requests = list()


class Message:
    def __init__(self, text, args=None):
        self.text = text
        self.args = args
    
    def __repr__(self):
        return f'Message(text={self.text}, args={self.args})'
    
    def __str__(self):
        return self.text


class DialogBot(object):

    def __init__(self, token, generator):
        self.updater = Updater(token=token)
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        self.updater.dispatcher.add_handler(handler)
        self.handlers = collections.defaultdict(generator)

    def start(self):
        self.updater.start_polling()

    def handle_message(self, bot, update):
        chat_id = update.message.chat_id

        if update.message.text == "/start":
            self.handlers.pop(chat_id, None)
        
        if chat_id in self.handlers:
            try:
                answer = self.handlers[chat_id].send(update.message)
            except StopIteration:
                del self.handlers[chat_id]
                return self.handle_message(bot, update)
        else:
            answer = next(self.handlers[chat_id])

        if answer.text == "Здравствуйте!\n Выберите пункт меню.":
            bot.sendMessage(chat_id=chat_id, text=answer.text, reply_markup=ReplyKeyboardMarkup([['Поиск ошибки по номеру', 'FAQ', 'Служба Поддержки']]), one_time_keyboard=True)
        elif answer.text[0] == '$':
            answer = answer[1:]
            bot.sendMessage(chat_id=-438860045, text=answer.text)
        else:
            if answer.args == None:
                bot.sendMessage(chat_id=chat_id, text=answer.text)
            else:
                args = answer.args
                if 'webhook_disable' in args.keys():
                    bot.deleteWebHook()
                bot.sendMessage(chat_id=chat_id, text=answer.text, **args)

        # bot.sendMessage(chat_id=274354611, text=answer)
        # bot.sendMessage(chat_id=-438860045, text=answer)


def dialog():
    """
        Main menu
    """
    answer = yield Message('Здравствуйте!\n Выберите пункт меню.')
    if answer.text == 'Поиск ошибки по номеру':
        answer = yield from error_number_grab()
    elif answer.text == 'FAQ':
        yield Message("Здесь будет любой FAQ.\n<b>Во всех сообщениях бота можно использовать HTML разметку и <i>Markdown</i> разметку</b>", {'reply_markup': ReplyKeyboardRemove(), 'parse_mode': 'HTML'})
    elif answer.text == 'Служба Поддержки':
        yield from support_request()
    elif answer.text == 'printr':
        answer = yield from print_requests()


def error_number_grab():
    """
        When user wants to search an information about error in database
    """

    answer = yield Message("Введите номер ошибки", {'reply_markup': ReplyKeyboardRemove()})
    num = answer.text
    try:
        con = pymysql.connect('localhost', 'root', 'Koordinator1414a', 'TestBase')
        cur = con.cursor()
        cur.execute(f"SELECT * FROM Errors WHERE Number={num}")
        record = cur.fetchone()
        con.close()
    except Exception as error:
        print(error)

    try:
        answer = yield Message(f'Number: {record[1]}\nDescription: {record[2]}\nHow to fix: {record[3]}')
    except:
        answer = yield Message('Данная ошибка не найдена в базе. Пожалуйста, повторите попытку.')


def support_request():
    """
        When user want to send request directly to staff.
    """

    answer = yield Message('Как вас зовут?', {'reply_markup': ReplyKeyboardRemove()})
    name = answer.text
    answer = yield Message('Пожалуйста, введите свой email, чтобы мы могли с Вами связаться.')
    email = answer.text
    answer = yield Message('Опишите проблему максимально подробно. Это сильно поможет её решить.')
    text = answer.text
    get(f'https://api.telegram.org/bot1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI/sendMessage?chat_id=-438860045&text=Name+{name.strip()}\nEmail:+{email.strip()}\nMessage:+{text.replace(" ", "+")}')
    requests.append(f'Name: {name}\nEmail: {email}\nMessage: {text}')
    yield Message('Отлично!\n Мы получили все необходимые сведения и отреагируем максимально оперативно. На указанную почту придёт письмо от персонала. \nДо скорой встречи!', {'webhook_disable': True})

def print_requests():
    """
        Shows requests (in server console), sent by "Support request" option in menu.
    """

    print(requests)
    answer = yield Message('Success printed to console.', {'reply_markup': ReplyKeyboardRemove()})
    return answer.text


if __name__ == "__main__":
    try:
        dialog_bot = DialogBot('1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI', dialog)
        dialog_bot.start()
    except Exception as error:
        print(error)
