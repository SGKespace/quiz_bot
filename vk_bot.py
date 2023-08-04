import os
import json
import redis
import random
import logging

import vk_api as vk
from dotenv import load_dotenv
from get_questions import fetch_questions
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

logger = logging.getLogger(__name__)
exception_logger = logging.getLogger('exception_logger')


def start(event, vk_api, keyboard):
    text = 'Привет! Я бот для викторин.'
    vk_api.messages.send(user_id=event.user_id, message=text, keyboard=keyboard.get_keyboard(), random_id=random.randint(1, 1000))


def ask_question(event, vk_api, keyboard, redis_client, quiz_questions):
    user_id = event.user_id
    quiz_question = random.choice(quiz_questions)
    redis_client.set(f'{user_id}_question', json.dumps(quiz_question))
    question = json.loads(redis_client.get(f'{user_id}_question'))
    logger.info(f'question--->{quiz_question[0]}, \n\nanswer--->{quiz_question[1]}')
    question_text = f'Внимание вопрос: \n\n{question[0]}'
    vk_api.messages.send(user_id=event.user_id, message=question_text, keyboard=keyboard.get_keyboard(), random_id=random.randint(1, 1000))


def check_answer(event, vk_api, keyboard, redis_client):
    user_id = event.user_id
    answer = json.loads(redis_client.get(f'{user_id}_question'))[1]
    lower_answer = answer.lower()
    if event.text.lower() == lower_answer:
        total_score = 0
        get_score = redis_client.get(f'{chat_id}_score')
        if not get_score:
            total_score = json.loads(get_score)
        redis_client.set(f'{user_id}_score', total_score + 1)
        bot_answer = 'Вы дали верный ответ. Выберите действие из меню'
    else:
        bot_answer = 'Вы дали не верный ответ. Попробуйте еще раз ответить или выберите действие из меню'
    vk_api.messages.send( user_id=event.user_id, message=bot_answer, keyboard=keyboard.get_keyboard(), random_id=random.randint(1, 1000))


def show_answer(event, vk_api, keyboard, redis_client, quiz_questions):
    user_id = event.user_id
    answer = json.loads(redis_client.get(f'{user_id}_question'))[1]
    bot_answer = f"Правильный ответ \n\n{answer}\n\n"
    vk_api.messages.send(user_id=event.user_id, message=bot_answer, keyboard=keyboard.get_keyboard(), random_id=random.randint(1, 1000))
    ask_question(event, vk_api, keyboard, redis_client, quiz_questions)


def check_score(event, vk_api, keyboard, redis_client):
    user_id = event.user_id
    total_score = json.loads(redis_client.get(f'{user_id}_score'))
    bot_answer = f"Ваш рейтинг  правильных ответов {total_score}"
    vk_api.messages.send(user_id=event.user_id, message=bot_answer, keyboard=keyboard.get_keyboard(), random_id=random.randint(1, 1000))


def handle_user_input(event, vk_api, redis_client, quiz_questions):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)
    if event.text == 'Новый вопрос':
        ask_question(event, vk_api, keyboard, redis_client, quiz_questions)
    elif event.text == 'Start':
        start(event, vk_api, keyboard)
    elif event.text == 'Сдаться':
        show_answer(event, vk_api, keyboard, redis_client, quiz_questions)
    elif event.text == 'Мой счет':
        check_score(event, vk_api, keyboard, redis_client)
    else:
        check_answer(event, vk_api, keyboard, redis_client)


def main() -> None:
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    vk_session = vk.VkApi(token=vk_token)
    questions_dir = os.getenv('QUESTIONS_DIR')
    quiz_questions = fetch_questions(questions_dir)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %I:%M:%S %p', level=logging.INFO)
    exception_logger.setLevel(logging.ERROR)
    logger.info(f'ВК-bot запущен.')

    with redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=0,
            password=os.getenv("REDIS_PASSWORD")
    ) as redis_client:
        while True:
            try:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        handle_user_input(event, vk_api, redis_client, quiz_questions)
            except Exception:
                exception_logger.exception("Ошибка ВК-bot")


if __name__ == "__main__":
    main()