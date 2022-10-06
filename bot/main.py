import os
import gspread
import yaml
import random
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
from helper import set_keyboard_small, set_keyboard_wide

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

with open(os.getcwd() + "/bot/strings.yaml", "r") as stream:
    strings = yaml.safe_load(stream)

SHEET_KEY = os.environ["sheet_key"]
SHEET_NAME_TECH = "tech"
SHEET_NAME_USERS = "users"
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
PARSE_MODE = "Markdown"

QUESTION = range(1)


def get_questions(sheet_key, sheet_name_tech, sheet_name_users, token, user, chat_id):
    gc = gspread.service_account_from_dict(token)
    sh = gc.open_by_key(sheet_key)
    worksheet = sh.worksheet(sheet_name_tech)

    users_sheet = sh.worksheet(sheet_name_users)
    users_list = users_sheet.col_values(1)
    chat_ids = users_sheet.col_values(2)
    user_info = dict(zip(users_list, chat_ids))
    user_info[user] = chat_id
    users_sheet.resize(1)
    users_sheet.clear()
    users_sheet.update(list(map(list, user_info.items())))

    questions = {key: value for (key, value) in enumerate(worksheet.get_all_values())}
    questions.pop(0)
    logger.info(f"User {user} loaded questions from Google")
    return questions


def start(update, context):
    context.user_data.clear()
    context.user_data["username"] = update.message.from_user["username"]
    context.user_data["right_count"] = 0
    context.user_data["wrong_count"] = 0

    logger.info(f"User {context.user_data['username']} called /start")

    context.user_data["questions"] = get_questions(
        SHEET_KEY,
        SHEET_NAME_TECH,
        SHEET_NAME_USERS,
        TOKEN,
        context.user_data["username"],
        update.message.chat_id,
    )

    update.message.reply_text(
        text=strings["quiz_start"].format(number=len(context.user_data["questions"])),
        parse_mode=PARSE_MODE,
    )

    return form_question(update, context)


def form_question(update, context):
    logger.info(
        f"User {context.user_data['username']} has {len(context.user_data['questions'])} unanswered questions"
    )

    if len(context.user_data["questions"]) == 0:
        update.message.reply_text(
            text=strings["quiz_finish"].format(
                right_count=context.user_data["right_count"],
                wrong_count=context.user_data["wrong_count"],
            ),
            parse_mode=PARSE_MODE,
        )
        logger.info(f"User {context.user_data['username']} ran out of questions")
        return ConversationHandler.END

    context.user_data["question_number"] = random.choice(
        list(context.user_data["questions"].keys())
    )
    logger.info(
        f"User {context.user_data['username']} rolled {context.user_data['question_number']} question"
    )

    data = list(
        map(str, context.user_data["questions"][context.user_data["question_number"]])
    )
    logger.info(f"User {context.user_data['username']} question data {data}")

    context.user_data["question"] = data.pop(0)
    context.user_data["answer"] = data[0]
    context.user_data["question_photo"] = data.pop()
    keyboard = None
    random.shuffle(data)

    if any([True for x in data if len(x) >= 32]):
        context.user_data["answer"] = str(data.index(context.user_data["answer"]) + 1)
        context.user_data["question"] = strings["long_question"].format(
            question=context.user_data["question"],
            option_0=data[0],
            option_1=data[1],
            option_2=data[2],
        )
        keyboard = set_keyboard_small("1", "2", "3")
    else:
        if any([True for x in data if len(x) >= 16]):
            keyboard = set_keyboard_wide(data[0], data[1], data[2])
        else:
            keyboard = set_keyboard_small(data[0], data[1], data[2])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if context.user_data["question_photo"]:
        with open(
            os.getcwd() + "/bot/images/" + context.user_data["question_photo"] + ".png",
            "rb",
        ) as image:
            update.message.reply_photo(
                photo=image,
                caption=context.user_data["question"],
                reply_markup=reply_markup,
            )
    else:
        update.message.reply_text(
            context.user_data["question"], reply_markup=reply_markup
        )
    return QUESTION


def answer_button(update, context):
    query = update.callback_query
    query.answer()

    edit_type, message_type = (
        ("edit_message_caption", "caption")
        if context.user_data["question_photo"]
        else ("edit_message_text", "text")
    )

    answer = (
        "right_answer" if query.data == context.user_data["answer"] else "wrong_answer"
    )

    getattr(query, edit_type)(
        **{
            message_type: strings[answer].format(
                question=context.user_data["question"],
                answer=context.user_data["answer"],
            ),
            "parse_mode": PARSE_MODE,
        }
    )

    if answer == "right_answer":
        context.user_data["right_count"] += 1
        context.user_data["questions"].pop(context.user_data["question_number"])
    else:
        context.user_data["wrong_count"] += 1

    logger.info(f"User {context.user_data['username']} got the {answer}")

    return form_question(query, context)


def help(update, context):
    update.message.reply_text(strings["help"], disable_web_page_preview=True)
    logger.info(f"User {update.message.from_user['username']} called help")


def cancel(update, context):
    update.message.reply_text(
        text=strings["quiz_finish"].format(
            right_count=context.user_data["right_count"],
            wrong_count=context.user_data["wrong_count"],
        ),
        parse_mode=PARSE_MODE,
    )
    logger.info(f"User {update.message.from_user['username']} called cancel")
    return ConversationHandler.END


def false_start(update, context):
    update.message.reply_text(strings["false_start"], parse_mode=PARSE_MODE)
    logger.info(f"User {update.message.from_user['username']} called false_start")


def false_cancel(update, context):
    update.message.reply_text(strings["false_cancel"], parse_mode=PARSE_MODE)
    logger.info(f"User {update.message.from_user['username']} called false_cancel")


def main(bot_token):
    updater = Updater(bot_token)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        allow_reentry=False,
        states={QUESTION: [CallbackQueryHandler(answer_button)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.dispatcher.add_handler(CommandHandler("start", false_start))
    updater.dispatcher.add_handler(CommandHandler("cancel", false_cancel))

    updater.dispatcher.add_handler(CommandHandler("help", help))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, help))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(BOT_TOKEN)
