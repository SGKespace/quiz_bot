import os
import re


def fetch_questions(quiz_questions_dir):
    questions = []
    questions_path = []

    for root, dirs, files in os.walk(quiz_questions_dir):
        for filename in files:
            questions_path.append(os.path.join(root, filename))

    for question_path in questions_path:
        with open(question_path, "r", encoding="KOI8-R") as file:
            file_contents = file.read()
        questions_info = file_contents.split('\n\n')
        for question_number, quiz_question in enumerate(questions_info):
            if 'Вопрос ' in quiz_question:
                question = re.sub(r'Вопрос \d+:\s+', '', quiz_question)
                try:
                    answer = re.sub(r'Ответ:\s+', '', questions_info[question_number + 1])
                except IndexError:
                    continue
                questions.append((question, answer[:-1]))
    return questions


def main():
    quiz_questions_dir = './quiz-questions'
    questions = fetch_questions(quiz_questions_dir)


if __name__ == '__main__':
    main()