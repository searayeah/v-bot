import os
import gspread
import yaml
from random import shuffle, choice

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
import logging

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
DONATE_NUMBER = os.environ["number"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)

with open("bot/strings.yaml", "r") as stream:
    strings = yaml.safe_load(stream)


def set_keyboard_small(x, y, z):
    return [
        [
            InlineKeyboardButton(x, callback_data=x),
            InlineKeyboardButton(y, callback_data=y),
        ],
        [
            InlineKeyboardButton(z, callback_data=z),
        ],
    ]


def set_keyboard_wide(x, y, z):
    return [
        [
            InlineKeyboardButton(x, callback_data=x),
        ],
        [
            InlineKeyboardButton(y, callback_data=y),
        ],
        [
            InlineKeyboardButton(z, callback_data=z),
        ],
    ]


def get_questions(sheet_key, sheet_name, token_names_list, token, user):
    gc = gspread.service_account_from_dict(token)
    sh = gc.open_by_key(sheet_key)
    worksheet = getattr(sh, sheet_name)
    log.info(f"User {user} loaded questions from Google")
    users_sheet = sh.get_worksheet(1)
    users_list = users_sheet.col_values(1)
    if user not in users_list:
        users_list.append(user)
        users_sheet.resize(1)
        users_sheet.clear()
        log.info(f"User {user} is NEW")
        users_sheet.update([users_list], major_dimension="COLUMNS")
    return {key: value for (key, value) in enumerate(worksheet.get_all_values())}


def start(update, context):
    context.user_data["user"] = update.message.from_user["username"]
    context.user_data["right_ans_qt"] = 0
    context.user_data["wrong_ans_qt"] = 0

    log.info(f"""User {context.user_data["user"]} called /start""")

    update.message.reply_text(strings["help_message"], parse_mode="markdown")

    context.user_data["qstns"] = get_questions(
        SHEET_KEY, SHEET_NAME, TOKEN_NAMES_LIST, TOKEN, context.user_data["user"]
    )
    context.user_data["qstns"].pop(0)

    update.message.reply_text(
        strings["start_message"].format(number=len(context.user_data["qstns"])),
        parse_mode="markdown",
    )

    return form_question(update, context)


def form_question(update, context):
    log.info(
        f"""User {context.user_data["user"]} has {len(context.user_data["qstns"])} unanswered questions"""
    )

    if len(context.user_data["qstns"]) == 0:
        update.message.reply_text(strings["ending_message"], parse_mode="markdown")
        log.info(
            f"""User {context.user_data["user"]} ran out of questions, calling /reset"""
        )
        return reset(update, context)

    context.user_data["quest_id"] = choice(list(context.user_data["qstns"].keys()))
    log.info(
        f"""User {context.user_data["user"]} rolled {context.user_data["quest_id"]} question"""
    )

    data = list(map(str, context.user_data["qstns"][context.user_data["quest_id"]]))
    log.info(f"""User {context.user_data["user"]} question data {data}""")

    context.user_data["quest"] = data.pop(0)
    context.user_data["ans"] = data[0]
    context.user_data["quest_photo"] = data.pop()
    keyboard = []
    shuffle(data)

    if any([True for x in data if len(x) >= 32]):
        context.user_data["ans"] = str(data.index(context.user_data["ans"]) + 1)
        context.user_data["quest"] = strings["long_question"].format(
            question=context.user_data["quest"],
            response0=data[0],
            response1=data[1],
            response2=data[2],
        )
        keyboard = set_keyboard_small("1", "2", "3")
    else:
        if any([True for x in data if len(x) >= 16]):
            keyboard = set_keyboard_wide(data[0], data[1], data[2])
        else:
            keyboard = set_keyboard_small(data[0], data[1], data[2])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if context.user_data["quest_photo"] != "":
        with open(
            "bot/images/" + context.user_data["quest_photo"] + ".png", "rb"
        ) as image:
            update.message.reply_photo(
                photo=image,
                caption=context.user_data["quest"],
                reply_markup=reply_markup,
            )
    else:
        update.message.reply_text(context.user_data["quest"], reply_markup=reply_markup)

    return QUESTION


def button(update, context):
    query = update.callback_query
    query.answer()

    edit_type, message_type = (
        ("edit_message_caption", "caption")
        if context.user_data["quest_photo"] != ""
        else ("edit_message_text", "text")
    )

    answer = (
        "right_answer" if query.data == context.user_data["ans"] else "wrong_answer"
    )

    getattr(query, edit_type)(
        **{
            message_type: strings[answer].format(
                question=context.user_data["quest"],
                answer=context.user_data["ans"],
            ),
            "parse_mode": "markdown",
        }
    )

    if answer == "right_answer":
        context.user_data["right_ans_qt"] += 1
        context.user_data["qstns"].pop(context.user_data["quest_id"])
    else:
        context.user_data["wrong_ans_qt"] += 1

    log.info(f"""User {context.user_data["user"]} got the {answer}""")

    return form_question(query, context)


def reset(update, context):
    log.info(f"""User {context.user_data["user"]} called reset""")
    stats(update, context)
    context.user_data.clear()
    update.message.reply_text(strings["reset_message"], parse_mode="markdown")
    return ConversationHandler.END


def stats(update, context):
    if "right_ans_qt" not in context.user_data:
        update.message.reply_text(strings["nothing_message"], parse_mode="markdown")
        log.info(f"""User called stats""")
    else:
        update.message.reply_text(
            strings["stats_message"].format(
                right_number=context.user_data["right_ans_qt"],
                wrong_number=context.user_data["wrong_ans_qt"],
                remaining_number=len(context.user_data["qstns"]),
            ),
            parse_mode="markdown",
        )
        log.info(f"""User {context.user_data["user"]} called stats""")


def extra(update, context):
    update.message.reply_text(strings["extra"], parse_mode="markdown")
    log.info(f"""User called extra""")


def commands(update, context):
    update.message.reply_text(strings["help"], parse_mode="markdown")
    log.info(f"""User called help""")


def donate(update, context):
    update.message.reply_text(
        strings["donate_message"].format(number=DONATE_NUMBER), parse_mode="markdown"
    )
    log.info(f"""User called donate""")


def false_start(update, context):
    update.message.reply_text(strings["false_start"], parse_mode="markdown")
    log.info(f"""User called false start""")


def false_reset(update, context):
    update.message.reply_text(strings["false_reset"], parse_mode="markdown")
    log.info(f"""User called false reset""")


def main(bot_token):
    updater = Updater(bot_token)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        allow_reentry=False,
        states={QUESTION: [CallbackQueryHandler(button)]},
        fallbacks=[CommandHandler("reset", reset)],
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.dispatcher.add_handler(CommandHandler("stats", stats))
    updater.dispatcher.add_handler(CommandHandler("extra", extra))
    updater.dispatcher.add_handler(CommandHandler("help", commands))
    updater.dispatcher.add_handler(CommandHandler("donate", donate))

    updater.dispatcher.add_handler(CommandHandler("start", false_start))
    updater.dispatcher.add_handler(CommandHandler("reset", false_reset))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, commands))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(BOT_TOKEN)
