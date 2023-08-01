import logging
from dotenv import load_dotenv
import os
import redis

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler


ANSWERS = range(1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    text = 'Привет! Я бот для викторин. Не хочешь играть сразу жми Сдаться'
    keyboard = [
        ["Новый вопрос", "Сдаться"],
                        ['Мой счет']
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(text=text, reply_markup=markup)

    return ANSWERS


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text('Напугался? Может попробуем еще раз?  Жми /start', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def question():
    return ANSWERS


def fail(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text('Напугался? Может попробуем еще раз?  Жми /start', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def score():
    return ANSWERS

def answer ():
    return ANSWERS



def main() -> None:
    load_dotenv()
    telegram_token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ['TG_CHAT_ID']

    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    redis_password = os.environ["REDIS_PASSWORD"]

    r = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_password)
    r.set(f'{chat_id}', 'bar')
    r.get('foo')

    updater = Updater(telegram_token)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ANSWERS: [
                MessageHandler(Filters.text("Новый вопрос"), question),
                MessageHandler(Filters.text("Сдаться"), fail),
                MessageHandler(Filters.text("Мой счет"), score),
                MessageHandler(Filters.text & ~Filters.command, answer)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()




if __name__ == '__main__':
    main()