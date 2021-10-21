import os
import pandas as pd
import numpy as np
import gspread
from random import shuffle

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
)

SHEET_KEY = os.environ["sheet_key"]
SHEET_NAME = "sheet1"
TOKEN_NAMES_LIST = [
    "type",
    "project_id",
    "private_key_id",
    "private_key",
    "client_email",
    "client_id",
    "auth_uri",
    "token_uri",
    "auth_provider_x509_cert_url",
    "client_x509_cert_url",
]
TOKEN = {item: os.environ[item].replace("\\n", "\n") for item in TOKEN_NAMES_LIST}
BOT_TOKEN = os.environ["bot_token"]


QUESTION, ANSWER = range(2)


def get_questions(sheet_key, sheet_name, token_names_list, token):
    gc = gspread.service_account_from_dict(token)
    sh = gc.open_by_key(sheet_key)
    worksheet = getattr(sh, sheet_name)
    return pd.DataFrame(worksheet.get_all_records())


def start(update, context):
    update.message.reply_text("Чтобы закончить пропишите /stop")
    global questions
    questions = get_questions(SHEET_KEY, SHEET_NAME, TOKEN_NAMES_LIST, TOKEN)
    form_question(update, context)
    return QUESTION


def form_question(update, context):
    random_number = np.random.randint(0, questions.shape[0])
    global data
    data = list(filter(None, questions.iloc[random_number].values))

    global question
    global answer
    question = data.pop(0)
    answer = data[0]
    keyboard = []
    print(data)
    if any([True for x in data if len(x) >= 60]):
        print("ENTERED")
        shuffle(data)
        answer = str(data.index(answer) + 1)
        question = f"{question} \n\n1.{data[0]}\n\n2.{data[1]}\n\n3.{data[2]}"
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data="1"),
                InlineKeyboardButton("2", callback_data="2"),
            ],
            [
                InlineKeyboardButton("3", callback_data="3"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(question, reply_markup=reply_markup)
    else:
        if len(data) == 3:
            shuffle(data)
            keyboard = [
                [
                    InlineKeyboardButton(str(data[0]), callback_data=str(data[0])),
                    InlineKeyboardButton(str(data[1]), callback_data=str(data[1])),
                ],
                [
                    InlineKeyboardButton(str(data[2]), callback_data=str(data[2])),
                ],
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(question, reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    query.answer()
    if query.data == answer:
        query.edit_message_text(
            text=question + "\n" + f"Верно - *{query.data}*",
            parse_mode="markdown",
        )
    else:
        query.edit_message_text(
            text=question + "\n\n" + f"Неверно!!! Правильный ответ - *{answer}*",
            parse_mode="markdown",
        )
    form_question(query, context)


def stop(update, context):
    update.message.reply_text("Пропишите /start, чтобы начать по новой")
    return ConversationHandler.END


def main(bot_token) -> None:

    updater = Updater(bot_token)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        allow_reentry=True,
        states={
            QUESTION: [
                CallbackQueryHandler(button),
            ],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(BOT_TOKEN)
