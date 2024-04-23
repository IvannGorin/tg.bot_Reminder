import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters)
from config import BOT_TOKEN, BOT_NAME

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

DATA = []
NAME, DESCRIPTION, THETYPE, ONCE = range(4)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_text(f"Здравствуй! Я {BOT_NAME}."
                                    f" Это пока что бета-версия, но с её развитием я расскажу о новых возможностях!")


async def reminder(update, context):
    await update.message.reply_text(f"Создается новый напоминатель.Введите название.")
    DATA.append({})
    return NAME

async def name(update, context):
    DATA[-1]['Name'] = update.message.text
    await update.message.reply_text("""Отлично. Напишите сообщение, которое вы получите при
                                        достижении времени.""")
    return DESCRIPTION


async def description(update, context):
    DATA[-1]['Description'] = update.message.text
    reply_keyboard = [["Разовый", "Цикличный"]]
    await update.message.reply_text("""Как скажите. Теперь выберите, какой вид напоминания вы бы хотели.""",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True), )
    return THETYPE


async def thetype(update, context):
    choice = update.message.text
    if choice == 'Разовый':
        DATA[-1]['Type'] = 'Once'
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text("""Стоит ли упомянуть заранее?""",
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True), )
        return ONCE
    elif choice == 'Цикличный':
        pass


async def once(update, context):
    choice = update.message.text
    if choice == 'Да':
        pass
    elif choice == 'Нет':
        pass


async def cancel(update, context):
    await update.message.reply_text(f'{DATA[-1]}')
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("reminder", reminder)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            THETYPE: [MessageHandler(filters.Regex("^(Разовый|Цикличный)$"), thetype)],
            ONCE: [MessageHandler(filters.Regex("^(Да|Нет)$"), once)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
