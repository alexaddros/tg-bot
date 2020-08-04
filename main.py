import collections
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram import ReplyKeyboardMarkup
import sys


class DialogBot(object):

    def __init__(self, token, generator):
        # updater -- переменная которая отвечает за связь с сервером Telegram'a и 
        # собственно даёт возможность получать сообщения
        self.updater = Updater(token=token)
        # задаём переменную handler, которая обрабатывает входящие сообщения, 
        # если они являются обычным текстом или командой (команда начинается с '/') 
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        # добаляем handler в updater, чтобы последний видел, что делать, если получил новое сообщение
        self.updater.dispatcher.add_handler(handler)
        # создаём словарь, в котором храним id чата и текущее состояние генератора диалога
        # (точку диалога, в котором находится конкретный чат)
        self.handlers = collections.defaultdict(generator)

    def start(self):
        self.updater.start_polling()

    def handle_message(self, bot, update):
        print("Received", update.message)
        chat_id = update.message.chat_id

        if update.message.text == "/start":
            # если передана команда /start, начинаем всё с начала -- для
            # этого удаляем состояние текущего чатика, если оно есть
            self.handlers.pop(chat_id, None)
        
        if chat_id in self.handlers:
            # если диалог уже начат, то надо использовать .send(), чтобы
            # передать в генератор ответ пользователя
            try:
                # отправляем в генератор 
                answer = self.handlers[chat_id].send(update.message)
            except StopIteration:
                # если при этом генератор закончился -- что делать, начинаем общение с начала
                del self.handlers[chat_id]

                # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
                return self.handle_message(bot, update)
        else:
            # диалог только начинается. defaultdict запустит новый генератор для этого
            # чатика, а мы должны будем извлечь первое сообщение с помощью .next()
            # (.send() срабатывает только после первого yield)
            answer = next(self.handlers[chat_id])

        # отправляем полученный ответ пользователю
        print("Answer: %r" % answer)
        if answer == 'Выберите:':
            variants = ['1', '2', '3']
            bot.sendMessage(chat_id=chat_id, text=answer, reply_markup=ReplyKeyboardMarkup([variants]))
        elif answer == 'Ваш файл.':
            with open('log.txt', 'rb') as doc:
                bot.send_document(chat_id, doc, caption=answer)
        elif answer[0] == '$':
            # bot.sendMessage(chat_id=274354611, text=answer) -- отправка в чат лично человеку
            bot.sendMessage(chat_id=-438860045, text=answer)
        else:
            pass


def dialog():
    answer = yield "Выберите:"
    choice = answer.text.strip()
    if choice == '1':
        answer = yield 'Тут допустим написано "Hello World!"'
    elif choice == '2':
        answer = yield 'Ваш файл.'
    elif choice == '3':
        answer = yield f'$ Пользователь {answer.chat.first_name + answer.chat.last_name} Обратился в службу поддержки.'


if __name__ == "__main__":
    dialog_bot = DialogBot('1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI', dialog)
    dialog_bot.start()
