import telebot
from os import environ

from dotenv import load_dotenv
load_dotenv()

bot = telebot.TeleBot(environ['apif'])
