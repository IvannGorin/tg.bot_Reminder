import telebot
from config import BOT_TOKEN, BOT_NAME
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime

bot = telebot.TeleBot(BOT_TOKEN)
DATA = []


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, f"""Привет! Я {BOT_NAME}, твой бот-напоминатель! Для помощи введите /ty\
torial""")


@bot.message_handler(commands=['tytorial'])
def tytorial(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton('/reminder')
    button2 = types.KeyboardButton('/info')
    button3 = types.KeyboardButton('/change')
    button4 = types.KeyboardButton('/remove')
    keyboard.add(button1, button2, button3, button4)
    bot.send_message(message.from_user.id, """Для создания нового напоминания введите /reminder.\nЧтобы посмотреть\
уже созданные напоминатели, введите /info.\nЧтобы изменить существующий, напишите команду /change.\nЧтобы удалить,введи\
те /remove.""", reply_markup=keyboard)


@bot.message_handler(commands=['info'])
def info(message):
    if len(DATA) == 0:
        bot.send_message(message.from_user.id, "Ни одного напоминателя ещё нет. Самое время добавить командой \
/reminder")
    else:
        for i in range(len(DATA)):
            bot.send_message(message.from_user.id, f"""Напоминатель №{i + 1}""")
            end(message, i)


@bot.message_handler(commands=['change'])
def change(message):
    if len(DATA) == 0:
        bot.send_message(message.from_user.id, "Пока что тут и менять нечего. Самое время это исправить командой /\
reminder.")
    else:
        info(message)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for i in range(1, len(DATA) + 1):
            button = types.KeyboardButton(i)
            keyboard.add(button)
        msg = bot.send_message(message.from_user.id, """Какой напоминатель вы хотите изменить?""",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, fp)


def fp(message):
    text = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in DATA[int(text) - 1].keys():
        button = types.KeyboardButton(i)
        keyboard.add(button)
    bot.send_message(message.from_user.id, """Какой параметр нужно изменить?""",
                            reply_markup=keyboard)
    pick(message, int(text) - 1)


def pick(message, i):
    text = message.text
    bot.send_message(message.from_user.id, message)
    # реализовать замену всех возможных элементов


@bot.message_handler(commands=['reminder'])
def reminder(message):
    msg = bot.send_message(message.chat.id, "Создается новый напоминатель. Введите название.")
    DATA.append({})
    bot.register_next_step_handler(msg, name)


def name(message):
    DATA[-1]['Name'] = message.text
    msg = bot.send_message(message.chat.id,
                           """Отлично. Напишите сообщение, которое вы получите при достижении времени.""")
    bot.register_next_step_handler(msg, thedate)


def thedate(message):
    DATA[-1]['Description'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton('Сегодня')
    button2 = types.KeyboardButton('Другая дата')
    keyboard.add(button1, button2)
    msg = bot.send_message(message.chat.id, """Напоминание нужно поставить на сегодня или на другую дату?""",
                           reply_markup=keyboard)
    bot.register_next_step_handler(msg, time)


def time(message):
    try:
        if message.text not in ['Сегодня', 'Другая дата']:
            raise TypeError
        if message.text == 'Сегодня':
            DATA[-1]['Date'] = datetime.date.today()
            msg = bot.reply_to(message, """Теперь введите час в формате 24, а затем минуту.""")
            bot.register_next_step_handler(msg, thetime)
        elif message.text == 'Другая дата':
            calendar, step = DetailedTelegramCalendar().build()
            bot.send_message(message.chat.id,
                             f"Select {LSTEP[step]}",
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
                    bot.edit_message_text(f"Вы выбрали {datetime.datetime.strftime(result, '%A, %B %d, %Y')}",
                                          c.message.chat.id,
                                          c.message.message_id)
                    if result < datetime.date.today():
                        bot.reply_to(message, 'Неверный формат ввода: дата не может быть в прошлом.')
                        calendar, step = DetailedTelegramCalendar().build()
                        bot.send_message(message.chat.id,
                                         f"Select {LSTEP[step]}",
                                         reply_markup=calendar)
                    else:
                        nice = True
                    if nice:
                        msg = bot.send_message(message.chat.id,
                                               """Теперь введите час в формате 24, а затем минуту. Пример: 15 53.""")
                        bot.register_next_step_handler(msg, thetime)
                DATA[-1]['Date'] = result
    except Exception as e:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton('Сегодня')
        button2 = types.KeyboardButton('Другая дата')
        keyboard.add(button1, button2)
        msg = bot.send_message(message.chat.id, """Выберите вариант даты.""", reply_markup=keyboard)
        bot.register_next_step_handler(msg, time)


def thetime(message):
    try:
        text = message.text.split()
        if not (0 <= int(text[0]) < 24 and 0 <= int(text[1]) < 60):
            raise TypeError
        DATA[-1]['hour'] = text[0]
        DATA[-1]['minute'] = text[1]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton('Разовый')
        button2 = types.KeyboardButton('Цикличный')
        keyboard.add(button1, button2)
        msg = bot.send_message(message.chat.id, """Напоминатель будет разовым или цикличным?""", reply_markup=keyboard)
        bot.register_next_step_handler(msg, thetype)
    except Exception as e:
        msg = bot.reply_to(message, "Неверный формат ввода. Требования ввода: Часы(0-23) минуты(0-59).")
        bot.register_next_step_handler(msg, thetime)


def thetype(message):
    try:
        if message.text not in ['Разовый', 'Цикличный']:
            raise TypeError
        if message.text == 'Разовый':
            DATA[-1]['Type'] = 'Разовый'
            bot.reply_to(message, f"""Прелестно. Посмотрим, что у нас получилось.""")
            end(message, -1)
        elif message.text == 'Цикличный':
            DATA[-1]['Type'] = 'Цикличный'
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button1 = types.KeyboardButton('Поминутный')
            button2 = types.KeyboardButton('Почасовой')
            button3 = types.KeyboardButton('Каждые несколько дней')
            keyboard.add(button1, button2, button3)
            msg = bot.send_message(message.chat.id, """Выберите вид цикла.""", reply_markup=keyboard)
            bot.register_next_step_handler(msg, morecertain)
    except Exception as e:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton('Разовый')
        button2 = types.KeyboardButton('Цикличный')
        keyboard.add(button1, button2)
        msg = bot.reply_to(message, """Выберите вид напоминателя из предложенных возможностей.""",
                           reply_markup=keyboard)
        bot.register_next_step_handler(msg, thetype)


def morecertain(message):
    try:
        if message.text not in ['Поминутный', 'Почасовой', 'Каждые несколько дней']:
            raise TypeError
        DATA[-1]['Frequency_type'] = message.text
        typesc = {'Поминутный': 'минут', 'Почасовой': 'часов', 'Каждые несколько дней': 'дней'}
        msg = bot.send_message(message.chat.id, f'Укажите конкретное количество {typesc[message.text]}.')
        bot.register_next_step_handler(msg, thecertain)
    except Exception:
        msg = bot.reply_to(message, """Неверный формат ввода. Выберите вид из списка.""")
        bot.register_next_step_handler(msg, morecertain)


def thecertain(message):
    try:
        if not (0 < int(message.text) <= 72):
            raise TypeError
        DATA[-1]['Frequency'] = message.text
        bot.send_message(message.chat.id, f"""Прелестно. Посмотрим, что у нас получилось.""")
        end(message, -1)
    except Exception:
        msg = bot.reply_to(message, """Неверный формат ввода. Требования ввода: Число(от 1 до 72)""")
        bot.register_next_step_handler(msg, thecertain)


def end(message, i):
    try:
        if DATA[i]['Type'] == 'Разовый':
            endtype = 'Разовый'
        else:
            if DATA[i]['Frequency_type'] == 'Поминутный':
                if int(DATA[-i]['Frequency']) == 1:
                    endtype = 'Каждую минуту.'
                elif 2 <= int(DATA[i]['Frequency']) <= 4:
                    endtype = f'Каждые {DATA[i]['Frequency']} минуты.'
                else:
                    endtype = f'Каждые {DATA[i]['Frequency']} минут.'
            elif DATA[i]['Frequency_type'] == 'Почасовой':
                if int(DATA[i]['Frequency']) == 1:
                    endtype = 'Каждый час.'
                elif 2 <= int(DATA[i]['Frequency']) <= 4:
                    endtype = f'Каждые {DATA[i]['Frequency']} часа.'
                else:
                    endtype = f'Каждые {DATA[i]['Frequency']} часов.'
            else:
                if int(DATA[i]['Frequency']) == 1:
                    endtype = 'Раз в день.'
                elif 2 <= int(DATA[i]['Frequency']) <= 4:
                    endtype = f'Каждые {DATA[i]['Frequency']} дня.'
                else:
                    endtype = f'Каждые {DATA[i]['Frequency']} дней.'
        bot.send_message(message.chat.id, f"""Название - {DATA[i]['Name']}\nОписание - \
{DATA[i]['Description']}\nДата - {datetime.datetime.strftime(DATA[i]['Date'], '%A, %B %d, %Y')}\nВремя - \
{DATA[i]['hour']}:{DATA[i]['minute']}\nЧастота - {endtype}""")
    except Exception:
        bot.send_message(message.chat.id, 'Упс, что то пошло не так')


bot.polling(none_stop=True)
