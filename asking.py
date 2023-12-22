# import telebot
import time
from sets import bot


data = {}

# message : telebot.types.Message


def ask(message, text: str, type: str = 'text'):
    """
    Ask a question and wait for an answer
    :param message: message from telebot
    :param text: question as a string
    :param type: the type of the data ex. text, image, ... as a string

    :return: the answer as a string
    """

    chat_id = message.chat.id
    data[chat_id] = {}
    data[chat_id]['type'] = type
    bot.send_message(chat_id, text)
    inputing(chat_id)
    while type not in data[chat_id]:
        time.sleep(1)
    text = data[chat_id]['text']
    del data[chat_id]
    return text


def inputing(chat_id):
    bot.register_next_step_handler_by_chat_id(chat_id, inputing_handler)


def inputing_handler(message):
    chat_id = message.chat.id
    if data[chat_id]['type'] == 'text':
        data[chat_id]['text'] = message.text
    elif data[chat_id]['type'] == 'image':
        data[chat_id]['image'] = message.photo[-1].file_id
    else:
        bot.register_next_step_handler_by_chat_id(chat_id, inputing_handler)
