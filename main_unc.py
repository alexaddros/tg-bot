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

        if answer.text == "Welcome!\n Choose menu option.":
            bot.sendMessage(chat_id=chat_id, text=answer.text, reply_markup=ReplyKeyboardMarkup([['Search error', 'FAQ', 'Support request']]), one_time_keyboard=True)
        elif answer.text[0] == '$':
            answer = answer[1:]
            bot.sendMessage(chat_id=-438860045, text=answer.text)
        else:
            if answer.args == None:
                bot.sendMessage(chat_id=chat_id, text=answer.text)
            else:
                args = answer.args
                bot.sendMessage(chat_id=chat_id, text=answer.text, **args)

        # bot.sendMessage(chat_id=274354611, text=answer)
        # bot.sendMessage(chat_id=-438860045, text=answer)


def dialog():
    """
        Main menu
    """
    answer = yield Message('Welcome!\n Choose menu option.')
    if answer.text == 'Search error':
        answer = yield from error_number_grab()
    elif answer.text == 'FAQ':
        yield Message("There are simple FAQ option.\n1. Robot or another product are not working?\n -- Try to reload it.\n2. You want to increase amount of product, transporting through the robot?\n -- You can't.", {'reply_markup': ReplyKeyboardRemove(), 'parse_mode': 'HTML'})
    elif answer.text == 'Support request':
        yield from support_request()
    elif answer.text == 'printr':
        answer = yield from print_requests()


def error_number_grab():
    """
        When user wants to search an information about error in database
    """

    answer = yield Message("Enter the error number", {'reply_markup': ReplyKeyboardRemove()})
    num = answer.text
    con = pymysql.connect('localhost', 'root', 'Koordinator1414a', 'TestBase')
    cur = con.cursor()
    record = cur.execute(f"SELECT * FROM Errors WHERE Number={num}")
    cur.submit()
    con.close()

    try:
        answer = yield Message(f'Number: {record[0]}\nDescription: {record[1]}\nHow to fix: {record[2]}')
    except:
        answer = yield Message('This error can not be found in database. Please, retry.')


def support_request():
    """
        When user want to send request directly to staff.
    """

    answer = yield Message('Ok, so, how should we call you?', {'reply_markup': ReplyKeyboardRemove()})
    name = answer.text
    answer = yield Message('Good. Now, please, write your e-mail, we will send you respond you as fast as we can.')
    email = answer.text
    answer = yield Message('Well, now please explain us, what kind of problem you have in details.')
    text = answer.text
    get(f'https://api.telegram.org/bot1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI/sendMessage?chat_id=-438860045&text=Name+{name.strip()}\nEmail:+{email.strip()}\nMessage:+{text.replace(" ", "+")}')
    requests.append(f'Name: {name}\nEmail: {email}\nMessage: {text}')
    yield Message('Perfect!\n We got all information that we need to solve your problem. We will send your an letter to the email ou specified earlier.\nSee you soon!')

def print_requests():
    """
        Shows requests (in server console), sent by "Support request" option in menu.
    """

    print(requests)
    answer = yield Message('Success printed to console.', {'reply_markup': ReplyKeyboardRemove()})
    return answer.text


if __name__ == "__main__":
    dialog_bot = DialogBot('1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI', dialog)
    dialog_bot.start()
