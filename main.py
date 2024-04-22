import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from config import BOT_TOKEN, BOT_NAME

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

DATA = []
NAME, DESCRIPTION, THETYPE = range(3)
async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_text(f"Здравствуй! Я {BOT_NAME}. Это пока что бета-версия, но с её развитием я расскажу о новых возможностях!")


async def reminder(update, context):
    await update.message.reply_text(f"Введите название напоминания.")
    DATA.append({})
    return NAME

async def name(update, context):
    DATA[-1]['Name'] = update.message.text
    await update.message.reply_text("""Отлично. Напишите сообщение, которое вы получите при
                                    достижении времени.""")
    return DESCRIPTION

async def description(update, context):
    DATA[-1]['Description'] = update.message.text
    await update.message.reply_text("""Как скажете. Теперь выберите, какой вид напоминания вы бы хотели.""")
    return THETYPE
async def cancel(update, context):
    await update.message.reply_text(f'{DATA[-1]}')
    return ConversationHandler.END

async def thetype(update, context):
    pass
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("reminder", reminder)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            THETYPE: [MessageHandler(filters.Regex("^(Цикличный|Разовый)$"), thetype)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()
