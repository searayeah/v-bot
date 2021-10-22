import os
import gspread
from random import shuffle, choice

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    PicklePersistence,
)
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)

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
QUESTION = range(1)


def get_questions(sheet_key, sheet_name, token_names_list, token):
    gc = gspread.service_account_from_dict(token)
    sh = gc.open_by_key(sheet_key)
    worksheet = getattr(sh, sheet_name)
    log.info("Loaded questions from google sheets")
    return {key: value for (key, value) in enumerate(worksheet.get_all_values())}


def set_keyboard(x, y, z):
    return [
        [
            InlineKeyboardButton(x, callback_data=x),
            InlineKeyboardButton(y, callback_data=y),
        ],
        [
            InlineKeyboardButton(z, callback_data=z),
        ],
    ]


def start(update, context):
    if "questions" not in context.user_data:
        context.user_data["questions"] = get_questions(
            SHEET_KEY, SHEET_NAME, TOKEN_NAMES_LIST, TOKEN
        )
        context.user_data["questions"].pop(0)
    update.message.reply_text(
        f"Чтобы ресетнуть список вопросов, пропишите /reset. "
        + f'У вас осталось *{len(context.user_data["questions"])}* нерешённых вопросов.'
        + " Список сам ресетится каждые 24 часа, "
        + "поэтому ваши решенные вопросы больше этого времени не сохранятся"
        + " (бесплатный хостинг вайпит серв каждые 24 часа)",
        parse_mode="markdown",
    )
    log.info("Start called")
    form_question(update, context)
    return QUESTION


def form_question(update, context):
    log.info(
        f'Form_question called with {len(context.user_data["questions"])} questions'
    )
    log.info(context.user_data["questions"])
    if len(context.user_data["questions"]) == 0:
        update.message.reply_text("*Вопросы кончились*", parse_mode="markdown")
        return reset(update, context)
    context.user_data["question_id"] = choice(
        list(context.user_data["questions"].keys())
    )
    log.info(f'Random question with number {context.user_data["question_id"]}')
    data = list(
        map(
            str,
            context.user_data["questions"][context.user_data["question_id"]],
        )
    )
    log.info(f"question data {data}")
    context.user_data["question"] = data.pop(0)
    context.user_data["answer"] = data[0]
    context.user_data["question_photo_url"] = data.pop()
    keyboard = []
    shuffle(data)
    if any([True for x in data if len(x) >= 60]):
        context.user_data["answer"] = str(data.index(context.user_data["answer"]) + 1)
        context.user_data[
            "question"
        ] = f'{context.user_data["question"]}\n\n1.{data[0]}\n\n2.{data[1]}\n\n3.{data[2]}'
        keyboard = set_keyboard("1", "2", "3")
    else:
        keyboard = set_keyboard(data[0], data[1], data[2])

    reply_markup = InlineKeyboardMarkup(keyboard)
    if context.user_data["question_photo_url"] != "":
        update.message.reply_photo(
            photo=context.user_data["question_photo_url"],
            caption=context.user_data["question"],
            reply_markup=reply_markup,
        )
    else:
        update.message.reply_text(
            context.user_data["question"], reply_markup=reply_markup
        )


def button(update, context):
    query = update.callback_query
    query.answer()
    if context.user_data["question_photo_url"] != "":
        if query.data == context.user_data["answer"]:
            query.edit_message_caption(
                caption=context.user_data["question"]
                + "\n\n"
                + f"Верно - *{query.data}*",
                parse_mode="markdown",
            )

            context.user_data["questions"].pop(context.user_data["question_id"])
            log.info(
                f"Right answer, dropping question from pool. "
                + f'Now pool size {len(context.user_data["questions"])}'
            )
        else:
            query.edit_message_caption(
                caption=context.user_data["question"]
                + "\n\n"
                + f'Неверно!!! Правильный ответ - *{context.user_data["answer"]}*',
                parse_mode="markdown",
            )
            log.info("Wrong answer")
    else:
        if query.data == context.user_data["answer"]:
            query.edit_message_text(
                text=context.user_data["question"] + "\n\n" + f"Верно - *{query.data}*",
                parse_mode="markdown",
            )

            context.user_data["questions"].pop(context.user_data["question_id"])
            log.info(
                f"Right answer, dropping question from pool. "
                + f'Now pool size {len(context.user_data["questions"])}'
            )
        else:
            query.edit_message_text(
                text=context.user_data["question"]
                + "\n\n"
                + f'Неверно!!! Правильный ответ - *{context.user_data["answer"]}*',
                parse_mode="markdown",
            )
            log.info("Wrong answer")
    form_question(query, context)


def reset(update, context):
    context.user_data.clear()
    update.message.reply_text("Пропишите /start, чтобы начать по новой")
    return ConversationHandler.END


def main(bot_token):
    persistence = PicklePersistence(filename="bot/base", store_callback_data=True)
    updater = Updater(bot_token, persistence=persistence, use_context=True)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        allow_reentry=True,
        states={QUESTION: [CallbackQueryHandler(button)]},
        fallbacks=[CommandHandler("reset", reset)],
        persistent=True,
        name="conv_handler_save",
    )
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(BOT_TOKEN)
