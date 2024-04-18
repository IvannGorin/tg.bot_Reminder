import logging

from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(f"Привет {user.mention_html()}! Я бот-напоминатель. Это пока что бета-версия, но с её развитием я расскажу о новых возможностях!")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == "__main__":
    main()
