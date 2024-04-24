import telebot
from config import BOT_TOKEN, BOT_NAME
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime

bot = telebot.TeleBot(BOT_TOKEN)
DATA = []


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Привет! Я {BOT_NAME}, твой бот-напоминатель!")


@bot.message_handler(commands=['reminder'])
def reminder(message):
    msg = bot.reply_to(message, "Создается новый напоминатель. Введите название.")
    DATA.append({})
    bot.register_next_step_handler(msg, name)


def name(message):
    DATA[-1]['Name'] = message.text
    msg = bot.reply_to(message, """Отлично. Напишите сообщение, которое вы получите при достижении времени.""")
    bot.register_next_step_handler(msg, thedate)


def thedate(message):
    DATA[-1]['Description'] = message.text
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Сегодня')
    button2 = types.KeyboardButton('Другая дата')
    keyboard.add(button1, button2)
    msg = bot.reply_to(message, """Напоминание нужно поставить на сегодня или на другую дату?""", reply_markup=keyboard)
    bot.register_next_step_handler(msg, time)


def time(message):
    if message.text == 'Сегодня':
        DATA[-1]['Date'] = datetime.date.today()
        msg = bot.reply_to(message, """Теперь введите час в формате 24, а затем минуту.""")
        bot.register_next_step_handler(msg, thetime)
    elif message.text == 'Другая дата':
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)

        @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
        def cal(c):
            nice = False
            result, key, step = DetailedTelegramCalendar().process(c.data)
            if not result and key:
                bot.edit_message_text(f"Select {LSTEP[step]}",
                                      c.message.chat.id,
                                      c.message.message_id,
                                      reply_markup=key)
            elif result:
                bot.edit_message_text(f"You selected {result}",
                                      c.message.chat.id,
                                      c.message.message_id)
                if result < datetime.date.today():
                    bot.reply_to(message, 'Неверный формат ввода: дата не может быть в прошлом')
                    calendar, step = DetailedTelegramCalendar().build()
                    bot.send_message(message.chat.id,
                                     f"Select {LSTEP[step]}",
                                     reply_markup=calendar)
                else:
                    nice = True
                if nice:
                    msg = bot.reply_to(message, """Теперь введите час в формате 24, а затем минуту. Пример: 15 53""")
                    bot.register_next_step_handler(msg, thetime)
            DATA[-1]['Date'] = result


def thetime(message):
    text = message.text
    DATA[-1]['hour'] = text.split()[0]
    DATA[-1]['minute'] = text.split()[1]
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Разовый')
    button2 = types.KeyboardButton('Цикличный')
    keyboard.add(button1, button2)
    msg = bot.reply_to(message, """Напоминатель будет разовым или цикличным?""", reply_markup=keyboard)
    bot.register_next_step_handler(msg, thetype)


def thetype(message):
    if message.text == 'Разовый':
        DATA[-1]['Type'] = 'Разовый'
        msg = bot.reply_to(message, f"""Прелестно. Посмотрим, что у нас получилось.\n{DATA[-1]}""")
        bot.register_next_step_handler(msg, done)
    elif message.text == 'Цикличный':
        DATA[-1]['Type'] = 'Цикличный'
        keyboard = types.ReplyKeyboardMarkup(row_width=2)
        button1 = types.KeyboardButton('Поминутный')
        button2 = types.KeyboardButton('Почасовой')
        button3 = types.KeyboardButton('Каждые несколько дней')
        keyboard.add(button1, button2, button3)
        msg = bot.reply_to(message, """Выберите частоту цикла.""", reply_markup=keyboard)
        bot.register_next_step_handler(msg, morecertain)


def morecertain(message):
    DATA[-1]['Frequency_type'] = message.text
    types = {'Поминутный': 'минут', 'Почасовой': 'часов', 'Каждые несколько дней': 'дней'}
    msg = bot.reply_to(message, f'Укажите конкретное количество {types[message.text]}')
    bot.register_next_step_handler(msg, MOREcertain)


def MOREcertain(message):
    DATA[-1]['Frequency'] = message.text
    msg = bot.reply_to(message, f"""Прелестно. Посмотрим, что у нас получилось.\n{DATA[-1]}""")
    bot.register_next_step_handler(msg, done)


def done(message):
    pass


bot.polling(none_stop=True)
