import telebot
from config import BOT_TOKEN, BOT_NAME
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
bot = telebot.TeleBot(BOT_TOKEN)
DATA = []


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Привет! Я {BOT_NAME}, твой бот-напоминатель!")


@bot.message_handler(commands=['reminder'])
def reminder(message):
    msg = bot.reply_to(message,"Создается новый напоминатель. Введите название.")
    DATA.append({})
    bot.register_next_step_handler(msg, name)


def name(message):
    DATA[-1]['Name'] = message.text
    msg = bot.reply_to(message,"""Отлично. Напишите сообщение, которое вы получите при достижении времени.""")
    bot.register_next_step_handler(msg, description)


def description(message):
    DATA[-1]['Description'] = message.text
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Разовый')
    button2 = types.KeyboardButton('Цикличный')
    keyboard.add(button1, button2)
    msg = bot.reply_to(message, """Как скажите. Теперь выберите, какой вид напоминания вы бы хотели.""",
                       reply_markup=keyboard)
    bot.register_next_step_handler(msg, type)


def type(message):
    DATA[-1]['Type'] = message.text
    if message.text == 'Разовый':
        keyboard = types.ReplyKeyboardMarkup(row_width=2)
        button1 = types.KeyboardButton('Да')
        button2 = types.KeyboardButton('Нет')
        keyboard.add(button1, button2)
        msg = bot.reply_to(message, 'Стоит ли упомянуть заранее?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, in_advance)
    elif message.text == 'Цикличный':
        pass


def in_advance(message):
    DATA[-1]['In_advance'] = message.text
    if message.text == 'Да':
        calendar, step = DetailedTelegramCalendar().build()
        msg = bot.send_message(message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)
    elif message.text == 'Нет':
        pass


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
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


bot.polling(none_stop=True)