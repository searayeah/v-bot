import logging
from telegram.ext import CommandHandler, filters, MessageHandler
from bot import application, strings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def help(update, context):
    await update.message.reply_text(strings["help"], disable_web_page_preview=True)
    logger.info(f"User {update.message.from_user['username']} called help")


application.add_handler(CommandHandler("help", help))

application.add_handler(MessageHandler(filters.TEXT, help))
