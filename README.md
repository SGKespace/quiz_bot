# quiz_bot
Боты для викторин в Телеграм и ВК.

## Требования к окружению

Получите токены  [Телеграм](https://t.me/BotFather), затем определите [chat_id](https://t.me/messageinformationsbot)  поместите в переменные окружения (файл .env). ВК: в меню управления сообщества на вкладке API.

Пример файла:

```
TELEGRAM_TOKEN="6357555438:AAjklnfnrfnl4rnfnv3nlvcnTFIrrTaWBJE8rkak4"
TG_CHAT_ID=1234567890
QUESTIONS_DIR='./quiz-questions'
REDIS_PASSWORD=sC1mOzyuuwGOvnvfnlrtkvnlscnmAQUw8G
REDIS_HOST=redis-18998.c84.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=18998
VK_TOKEN='vk1.a.lDTH179uc9-5n92UA9_lkOxEP5JxF-ZtW.m,dsnfkln435tak6yosrqEKvGCWWtTeuCx9R8BuiOHvRiRegwrbgrewgwpbx4k1E79Qs9PKbBY-a3BgibBt94RnkIUKBtLtwEltKtfblh7eF0lZEv0e4usc74Cfc_YG-z3ZDYvfljnljkKLJHHLKHJ793kjn,ahdk.vdnsAGwFkXhLMsdYsmZ9U5lczxZlw'

``` 

Python 3.xx и выше (должен быть уже установлен)

``` 
python-dotenv==1.0.0
python-telegram-bot==13.14
redis==4.5.2
vk-api==11.9.9
``` 

Можно установить командой  
``` 
PIP install -r requirements.txt
```

Запускать ботов осууществляетс с помощью команд

``` 
python tg_bot.py
python vk_bot.py
```

###База данных   Redislabs (https://redislabs.com/)   работает только через VPN

Для работы ботов нужны воппросы и ответы, [вы можете воспользоваться этими](https://dvmn.org/media/modules_dist/quiz-questions.zip)

## Отказ от ответственности

Автор программы не несет никакой ответственности за то, как вы используете этот код или как вы используете сгенерированные с его помощью данные. Эта программа была написана для обучения автора и других целей не несет. Не используйте данные, сгенерированные с помощью этого кода в незаконных целях.
