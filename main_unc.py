# -*- coding: utf-8 -*-

import collections
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram import ReplyKeyboardMarkup
import pymysql
import sys


class DialogBot(object):

    def __init__(self, token, generator):
        self.updater = Updater(token=token)
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        self.updater.dispatcher.add_handler(handler)
        self.handlers = collections.defaultdict(generator)

    def start(self):
        self.updater.start_polling()

    def handle_message(self, bot, update):
        print("Received", update.message)
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
        print("Answer: %r" % answer)
        bot.sendMessage(chat_id=chat_id, text=answer)
        # bot.sendMessage(chat_id=274354611, text=answer)
        # bot.sendMessage(chat_id=-438860045, text=answer)

def dialog():
    answer = yield "Welcome! Enter the error number"
    num = answer.text
    con = pymysql.connect('localhost', 'root', 'Koordinator1414a', 'TestBase')
    cur = con.cursor()
    record = cur.execute(f"SELECT * FROM Errors WHERE Number={num}")
    cur.submit()
    con.close()
    try:
        answer = yield f'Number: {record[0]}\nDescription: {record[1]}\nHow to fix: {record[2]}'
    except:
        answer = yield 'This error can not be found in database. Please, retry.'

def ask_yes_or_no(question):
    answer = yield question
    while not ("да" in answer.text.lower() or "нет" in answer.text.lower()):
        answer = yield "Так да или нет?"
    return "да" in answer.text.lower()


if __name__ == "__main__":
    dialog_bot = DialogBot('1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI', dialog)
    dialog_bot.start()
