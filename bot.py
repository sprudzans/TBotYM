import requests
import telebot
from telebot import types

API_TOKEN = "API_TOKEN"
bot = telebot.TeleBot("API_TOKEN")
user_dict = {}

class Question:
    def __init__(self, data):
        self.time = data

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, "Укажите за какое кол-во дней показать источники и переходы:")
    bot.register_next_step_handler(msg, process_time_step)


def process_time_step(message):
    chat_id = message.chat.id
    data = message.text
    if not data.isdigit():
        for word in data.split():
                if word.isdigit():
                    data = int(word)
    if data.isdigit():
        user = Question(data)
        user_dict[chat_id] = user
        try:
            response = requests.get(
                'https://api-metrika.yandex.net/stat/v1/data?date1='+user.time+'daysAgo&date2=today&dimensions=ym:s:firstSourceEngine&metrics=ym:s:visits,ym:s:avgVisitDurationSeconds,ym:s:bounceRate,ym:s:upToWeekUserRecencyPercentage&ids={{ids}}&pretty=true',
                headers={'Authorization': 'OAuth {{CODE}}', 'Accept-Language': 'ru'}
            )
            text = response.json()
            answer = '';
            for obj in text['data']:
                name = obj['dimensions'][0]['name']
                view = round(obj['metrics'][0], 2)
                time = round(obj['metrics'][1], 2)
                fail = round(obj['metrics'][2], 2)
                back = round(obj['metrics'][3], 2)
                answer += str(name) + ': ' + str(view) + '\n' + 'Время ' + str(time) + '\nОтказы: ' + str(fail) + '\nВозраты ' + str(back) + '\n\n'
            bot.send_message(chat_id, answer)
        except Exception as e:
            bot.reply_to(message, 'ERROR_RESPONSIVE')
    else:
        msg = bot.reply_to(message, 'Укажите только кол-во дней (цифрами):')
        bot.register_next_step_handler(msg, process_time_step)
        return


bot.polling()
