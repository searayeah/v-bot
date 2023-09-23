from telegram import Update
from bot import application
from bot.modules import quiz, help


def main():
    application.run_polling(allowed_updates=Update.ALL_TYPES)


main()
