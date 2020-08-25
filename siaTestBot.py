import telebot
from telebot import types


token = '1259925974:AAH3PsqjF16ic-079HhA-kDtCB8AKRtG_ZI'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['error'])
def errorNumber(message):
    bot.send_message(message.chat.id, 'Я помогу тебе, найти описание ошибки по номеру.')


@bot.message_handler(commands=['faq'])
def faq(message):
    bot.send_message(message.chat.id, 'Тут ответы на часто возникающие проблемы.')


@bot.message_handler(commands=['message'])
def message(message):
    bot.send_message(message.chat.id, 'Вы можите отправить сообщение инженерам.\nНапишите его прямо сйечас.')


@bot.message_handler(content_types=['message'])
def number_request(message):
    bot.send_message(message.chat.id, f'Your Error ID: {message.text}')


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, '/error - Для помощи.\n /faq - Часто задаваемые вопросы.\n /message - Для '
                                      'обращения в сервис.\n')


if __name__ == '__main__':
    bot.polling(none_stop=True)
