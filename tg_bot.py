import json
import logging
import os
import random
import redis

from functools import partial
from time import sleep
from dotenv import load_dotenv
from logs_handler import TelegramLogsHandler
from get_questions import fetch_questions

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler


logger = logging.getLogger(__name__)
exception_logger = logging.getLogger('exception_logger')

QUESTIONS, ANSWERS = 1, 2


def start(update: Update, context: CallbackContext) -> None:

    text = 'Привет! Я бот для викторин. Не хочешь играть сразу жми Сдаться'

    message_keyboard = [["Начать"],
                        ['Сдаться без боя']]

    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    context.user_data["score"] = 0
    update.message.reply_text(text=text, reply_markup=markup)
    return QUESTIONS


def ask_question(update: Update, context: CallbackContext, redis_client, quiz_questions):
    quiz_question = random.choice(quiz_questions)
    chat_id = update.effective_message.chat_id
    redis_client.set(f'{chat_id}_question', json.dumps(quiz_question))

    logger.info(f'question--->{quiz_question[0]}, \n answer--->{quiz_question[1]}')

    bot_answer = f'Вопрос на засыпку: \n\n{quiz_question[0]}'

    message_keyboard = [["Новый вопрос", "Сдаться"],
                        ["Мой счет", 'Выйти  из бота']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(bot_answer, reply_markup=markup)
    return ANSWERS


def check_answer(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id
    user_answer = update.effective_message.text.lower()
    answer = json.loads(redis_client.get(f'{chat_id}_question'))[1]
    lower_answer = answer.lower()
    if user_answer == lower_answer:
        context.user_data["score"] += 1
        try:
            total_score = json.loads(redis_client.get(f'{chat_id}_score'))
        except TypeError:
            total_score = 0
        redis_client.set(f'{chat_id}_score', total_score + 1)
        bot_answer = 'Вы дали верный ответ. Выберите действие из меню'
    else:
        bot_answer = 'Вы дали не верный ответ. Попробуйте еще раз ответить или выберите действие из меню'

    message_keyboard = [["Новый вопрос", "Сдаться"],
                        ["Мой счет", 'Выйти  из бота']]
    markup = ReplyKeyboardMarkup(
        message_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    update.message.reply_text(bot_answer, reply_markup=markup)
    return ANSWERS


def show_answer(update: Update, context: CallbackContext, redis_client, quiz_questions):
    score = context.user_data["score"]
    chat_id = update.effective_message.chat_id
    answer = json.loads(redis_client.get(f'{chat_id}_question'))[1]
    bot_answer = f'Правильный ответ \n\n{answer},\n\nВаш рейтинг  правильных ответов {score}'
    update.message.reply_text(bot_answer)
    ask_question(update, context, redis_client, quiz_questions)


def check_score(update: Update, context: CallbackContext, redis_client):
    chat_id = update.effective_message.chat_id
    score = context.user_data["score"]
    total_score = json.loads(redis_client.get(f'{chat_id}_score'))
    bot_answer = f"Ваш рейтинг текущей игры:  правильных ответов {score}. \n\n" \
                 f"Ваш общий  рейтинг:  правильных ответов {total_score}."
    message_keyboard = [["Новый вопрос", "Сдаться"],
                        ["Мой счет", 'Выйти  из бота']]
    markup = ReplyKeyboardMarkup(
        message_keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    update.message.reply_text(bot_answer, reply_markup=markup)
    return QUESTIONS


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    text = 'Работа бота завершена. Чтобы возобновить наберите /start'
    update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    load_dotenv()
    chat_id = os.getenv('TG_CHAT_ID')
    api_tg_token = os.getenv("TELEGRAM_TOKEN")
    questions_dir = os.getenv('QUESTIONS_DIR')

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                               '%(message)s', datefmt='%d-%m-%Y %I:%M:%S %p',
                        level=logging.INFO)

    quiz_questions = fetch_questions(questions_dir)

    exception_logger.setLevel(logging.ERROR)
    exception_logger.addHandler(TelegramLogsHandler(api_tg_token, chat_id))

    with redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=0,
            password=os.getenv("REDIS_PASSWORD")
    ) as redis_client:

        question = partial(ask_question, redis_client=redis_client, quiz_questions=quiz_questions)
        answer = partial(check_answer, redis_client=redis_client)
        fail = partial(show_answer, redis_client=redis_client, quiz_questions=quiz_questions)
        score = partial(check_score, redis_client=redis_client)

        updater = Updater(api_tg_token)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                QUESTIONS: [
                    MessageHandler(Filters.text("Начать"), question),
                    MessageHandler(Filters.text("Сдаться без боя"), cancel),
                ],
                ANSWERS: [
                    MessageHandler(Filters.text("Новый вопрос ❔"), question),
                    MessageHandler(Filters.text("Сдаться"), fail),
                    MessageHandler(Filters.text("Мой счет"), score),
                    MessageHandler(Filters.text("Выйти  из бота"), cancel),
                    MessageHandler(Filters.text & ~Filters.command, answer)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher = updater.dispatcher
        dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()