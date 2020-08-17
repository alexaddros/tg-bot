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
        if answer == 'Выберите:':
            variants = ['1', '2', '3']
            bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=ReplyKeyboardMarkup([variants]))
        elif answer == 'Ваш файл.':
            with open('log.txt', 'rb') as doc:
                bot.send_document(chat_id, doc, caption=answer)
        elif answer[0] == '$':
            bot.sendMessage(chat_id=274354611, text=answer)
            # bot.sendMessage(chat_id=-438860045, text=answer)
        else:
            pass


def dialog():
    answer = yield "Выберите:"
    choice = answer.text.strip()
    if choice == '1':
        answer = yield from number_request()
    elif choice == '2':
        answer = yield 'Ваш файл.'
    elif choice == '3':
        answer = yield f'$ Пользователь {answer.chat.username} Обратился в службу поддержки.'


def number_request():
    con = pymysql.connect('localhost', 'root', 'Koordinator1414a', 'TestBase')
    cur = con.cursor()
    answer = yield 'Введите номер ошибки'
    answer = answer.strip()
    try:
        cur.execute(f'SELECT * FROM Errors WHERE Number={answer}')
        record = cur.fetchone()
    except:
        return 'Данный номер не найден в базе. Повторите попытку.'

    return f'Number: {record[0]}\nDescription: {record[1]}\n How to fix: {record[2]}'


if __name__ == "__main__":
    dialog_bot = DialogBot('1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI', dialog)
    dialog_bot.start()
