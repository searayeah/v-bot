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
DONATE_NUMBER = os.environ["number"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)

with open("bot/strings.yaml", "r") as stream:
    strings = yaml.safe_load(stream)


# KEYBOARDS
def set_keyboard_1(x, callback_x):
    return [
        [
            InlineKeyboardButton(x, callback_data=str(callback_x)),
        ],
    ]


def set_keyboard_row_3(
    x,
    y,
    z,
    callback_x,
    callback_y,
    callback_z,
):
    return [
        [
            InlineKeyboardButton(x, callback_data=str(callback_x)),
            InlineKeyboardButton(y, callback_data=str(callback_y)),
            InlineKeyboardButton(z, callback_data=str(callback_z)),
        ]
    ]


def set_keyboard_list_3(
    x,
    y,
    z,
    callback_x,
    callback_y,
    callback_z,
):
    return [
        [
            InlineKeyboardButton(x, callback_data=str(callback_x)),
        ],
        [
            InlineKeyboardButton(y, callback_data=str(callback_y)),
        ],
        [
            InlineKeyboardButton(z, callback_data=str(callback_z)),
        ],
    ]


def set_keyboard_triangle_3(
    x,
    y,
    z,
    callback_x,
    callback_y,
    callback_z,
):
    return [
        [
            InlineKeyboardButton(x, callback_data=str(callback_x)),
            InlineKeyboardButton(y, callback_data=str(callback_y)),
        ],
        [
            InlineKeyboardButton(z, callback_data=str(callback_z)),
        ],
    ]


def set_keyboard_square_4(
    x,
    y,
    z,
    t,
    callback_x,
    callback_y,
    callback_z,
    callback_t,
):
    return [
        [
            InlineKeyboardButton(x, callback_data=str(callback_x)),
            InlineKeyboardButton(y, callback_data=str(callback_y)),
        ],
        [
            InlineKeyboardButton(z, callback_data=str(callback_z)),
            InlineKeyboardButton(t, callback_data=str(callback_t)),
        ],
    ]


def set_keyboard_square_5(
    x,
    y,
    z,
    t,
    s,
    callback_x,
    callback_y,
    callback_z,
    callback_t,
    callback_s,
):
    return [
        [
            InlineKeyboardButton(x, callback_data=str(callback_x)),
            InlineKeyboardButton(y, callback_data=str(callback_y)),
        ],
        [
            InlineKeyboardButton(z, callback_data=str(callback_z)),
            InlineKeyboardButton(t, callback_data=str(callback_t)),
        ],
        [
            InlineKeyboardButton(s, callback_data=str(callback_s)),
        ],
    ]


USER_STARTED, USER_ID = range(2)
(
    SELECTING_MAIN,
    SELECTING_EXAM,
    VIEWING_STICKER_PACKS,
    DONATING,
    SUBMITTING_BUG,
) = range(2, 7)
(
    VIEWING_TECH,
    VIEWING_COMPLEX,
    VIEWING_FIRE2,
) = range(7, 10)
(
    STARTING_TECH,
    VIEWING_TECH_STATS,
    VIEWING_TECH_EXTRA,
    RESETTING_TECH,
    VIEWING_TECH_FINISH,
) = range(10, 15)
(
    TECH_QSTN_STATE,
    TECH_QSTNS,
    TECH_NUM_RIGHT_ANS,
    TECH_NUM_WRONG_ANS,
    TECH_QSTN_ID,
    TECH_QSTN,
    TECH_ANS,
    TECH_QSTN_PHOTO,
) = range(15, 23)

(
    VIEWING_COMPLEX,
    VIEWING_FIRE2,
) = range(23, 25)
END = ConversationHandler.END


# MAIN
def save_user(sheet_key, sheet_name_users, token, user, chat_id):
    gc = gspread.service_account_from_dict(token)
    sh = gc.open_by_key(sheet_key)
    users_sheet = sh.worksheet(sheet_name_users)
    users_list = users_sheet.col_values(1)
    chat_ids = users_sheet.col_values(2)
    user_info = dict(zip(users_list, chat_ids))
    user_info[user] = chat_id
    users_sheet.resize(1)
    users_sheet.clear()
    users_sheet.update(list(map(list, user_info.items())))
    log.info(f"User {user} saved to Google")


def start_main(update, context):
    keyboard = set_keyboard_square_5(
        *strings["main"],
        SELECTING_EXAM,
        VIEWING_STICKER_PACKS,
        DONATING,
        SUBMITTING_BUG,
        END,
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    if context.user_data.get(USER_STARTED):
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=strings["main_start"],
            reply_markup=reply_markup,
            parse_mode="markdown",
        )
    else:
        update.message.reply_text(
            text=strings["main_start"],
            reply_markup=reply_markup,
            parse_mode="markdown",
        )

        context.user_data[USER_ID] = update.message.from_user["username"]

        save_user(
            SHEET_KEY,
            SHEET_NAME_USERS,
            TOKEN,
            context.user_data[USER_ID],
            update.message.chat_id,
        )

        context.user_data[USER_STARTED] = True

    log.info(f"User {context.user_data[USER_ID]} called main_start")
    return SELECTING_MAIN


def select_exam(update, context):
    update.callback_query.answer()
    keyboard = set_keyboard_square_4(
        *strings["exams"],
        strings["back"],
        VIEWING_TECH,
        VIEWING_COMPLEX,
        VIEWING_FIRE2,
        END,
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=strings["exams_select"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called select_exam")
    return SELECTING_EXAM


def end_exam_selecting(update, context):
    log.info(f"User {context.user_data[USER_ID]} called end_exam_selecting")
    start_main(update, context)
    return END


def view_sticker_packs(update, context):
    update.callback_query.answer()
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=strings["sticker_packs"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called view_sticker_packs")
    return VIEWING_STICKER_PACKS


def submit_bug(update, context):
    update.callback_query.answer()
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=strings["bug"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called submit_bug")
    return SUBMITTING_BUG


def donate(update, context):
    update.callback_query.answer()
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=strings["donate"].format(number=DONATE_NUMBER),
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called donate")
    return DONATING


def stop(update, context):
    context.user_data.clear()
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=strings["mashtak"],
        parse_mode="markdown",
    )
    return END


# TECH
def get_tech_questions(sheet_key, sheet_name_tech, token, user):
    gc = gspread.service_account_from_dict(token)
    sh = gc.open_by_key(sheet_key)
    worksheet = sh.worksheet(sheet_name_tech)

    log.info(f"User {user} called get_tech_questions")
    return {key: value for (key, value) in enumerate(worksheet.get_all_values())}


def reset_tech_data(context):
    temp_user_id = context.user_data[USER_ID]
    temp_user_started = context.user_data[USER_STARTED]
    context.user_data.clear()
    context.user_data[USER_ID] = temp_user_id
    context.user_data[USER_STARTED] = temp_user_started
    log.info(f"User {context.user_data[USER_ID]} resetted his tech data")


def start_tech(update, context):
    keyboard = set_keyboard_square_5(
        *strings["tech"],
        strings["back"],
        STARTING_TECH,
        VIEWING_TECH_STATS,
        VIEWING_TECH_EXTRA,
        RESETTING_TECH,
        END,
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    if context.user_data.get(USER_STARTED):
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=strings["tech_start"],
            reply_markup=reply_markup,
            parse_mode="markdown",
        )
    else:
        update.message.reply_text(
            text=strings["tech_start"],
            reply_markup=reply_markup,
            parse_mode="markdown",
        )

        if context.user_data.get(TECH_QSTN_STATE):
            context.user_data[TECH_QSTN_STATE] = False

        context.user_data[USER_STARTED] = True

    log.info(f"User {context.user_data[USER_ID]} called start_tech")
    return VIEWING_TECH


def tech_test(update, context):
    if context.user_data.get(TECH_QSTNS) is not None:
        if len(context.user_data[TECH_QSTNS]) == 0:
            reset_tech_data(context)

    # First tech_test message
    if context.user_data.get(TECH_QSTN_STATE) is None:
        context.user_data[TECH_QSTNS] = get_tech_questions(
            SHEET_KEY, SHEET_NAME_TECH, TOKEN, context.user_data[USER_ID]
        )
        context.user_data[TECH_QSTNS].pop(0)

        context.user_data[TECH_QSTN_STATE] = True
        context.user_data[TECH_NUM_RIGHT_ANS] = 0
        context.user_data[TECH_NUM_WRONG_ANS] = 0

        update.callback_query.answer(text="Ебашь")
        update.callback_query.edit_message_text(
            strings["tech_test_start"].format(
                number=len(context.user_data[TECH_QSTNS])
            ),
            parse_mode="markdown",
        )

    elif context.user_data.get(TECH_QSTN_STATE) is False:
        context.user_data[TECH_QSTN_STATE] = True

        update.callback_query.answer(text="Ебашь")
        update.callback_query.edit_message_text(
            strings["tech_test_cont"].format(number=len(context.user_data[TECH_QSTNS])),
            parse_mode="markdown",
        )

    # Getting random question
    context.user_data[TECH_QSTN_ID] = choice(list(context.user_data[TECH_QSTNS].keys()))
    data = list(
        map(str, context.user_data[TECH_QSTNS][context.user_data[TECH_QSTN_ID]])
    )
    context.user_data[TECH_QSTN] = data.pop(0)
    context.user_data[TECH_ANS] = data[0]
    context.user_data[TECH_QSTN_PHOTO] = data.pop()
    keyboard = []
    shuffle(data)

    # Setting button-answer type
    if any([True for x in data if len(x) >= 32]):
        context.user_data[TECH_ANS] = str(data.index(context.user_data[TECH_ANS]) + 1)
        context.user_data[TECH_QSTN] = strings["tech_test_long_qstn"].format(
            question=context.user_data[TECH_QSTN],
            option0=data[0],
            option1=data[1],
            option2=data[2],
        )
        keyboard = set_keyboard_row_3(
            *strings["tech_test_options"], *strings["tech_test_options"]
        )
    else:
        if any([True for x in data if len(x) >= 16]):
            keyboard = set_keyboard_list_3(*data, *data)
        else:
            keyboard = set_keyboard_triangle_3(*data, *data)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Displaying question
    if context.user_data[TECH_QSTN_PHOTO] != "":
        with open(
            "bot/images/" + context.user_data[TECH_QSTN_PHOTO] + ".png", "rb"
        ) as image:
            update.callback_query.message.reply_photo(
                photo=image,
                caption=context.user_data[TECH_QSTN],
                reply_markup=reply_markup,
            )
    else:
        update.callback_query.message.reply_text(
            context.user_data[TECH_QSTN], reply_markup=reply_markup
        )

    context.user_data[USER_STARTED] = False

    log.info(f"User {context.user_data[USER_ID]} called tech_test")
    log.info(
        f"User {context.user_data[USER_ID]} showing "
        + f"{context.user_data[TECH_QSTN_ID]} question"
    )
    return STARTING_TECH


def tech_test_buttons(update, context):
    query = update.callback_query
    query.answer()

    edit_type, message_type = (
        ("edit_message_caption", "caption")
        if context.user_data[TECH_QSTN_PHOTO] != ""
        else ("edit_message_text", "text")
    )

    answer = (
        "tech_test_right_ans"
        if query.data == context.user_data[TECH_ANS]
        else "tech_test_wrong_ans"
    )
    print("lolo")

    getattr(query, edit_type)(
        **{
            message_type: strings[answer].format(
                question=context.user_data[TECH_QSTN],
                answer=context.user_data[TECH_ANS],
            ),
            "parse_mode": "markdown",
        }
    )

    print("lol1")

    if answer == "tech_test_right_ans":
        context.user_data[TECH_NUM_RIGHT_ANS] += 1
        context.user_data[TECH_QSTNS].pop(context.user_data[TECH_QSTN_ID])
    else:
        context.user_data[TECH_NUM_WRONG_ANS] += 1

    log.info(f"User {context.user_data[USER_ID]} got the {answer}")
    if len(context.user_data[TECH_QSTNS]) == 0:
        log.info(f"User {context.user_data[USER_ID]} ran out of questions")
        tech_finish(update, context)
    else:
        print("lol2")
        tech_test(update, context)


def tech_stats(update, context):
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)

    if context.user_data.get(TECH_QSTN_STATE) is None:
        update.callback_query.edit_message_text(
            strings["tech_stats_nothing"],
            reply_markup=reply_markup,
            parse_mode="markdown",
        )
    else:
        update.callback_query.edit_message_text(
            strings["tech_stats"].format(
                right_number=context.user_data[TECH_NUM_RIGHT_ANS],
                wrong_number=context.user_data[TECH_NUM_WRONG_ANS],
                remaining_number=len(context.user_data[TECH_QSTNS]),
            ),
            reply_markup=reply_markup,
            parse_mode="markdown",
        )

    log.info(f"User {context.user_data[USER_ID]} called tech_stats")
    return VIEWING_TECH_STATS


def tech_extra(update, context):
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        strings["tech_extra"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called tech_extra")
    return VIEWING_TECH_EXTRA


def tech_reset(update, context):
    reset_tech_data(context)
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        strings["tech_reset"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called tech_reset")
    return RESETTING_TECH


def tech_finish(update, context):
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text(
        strings["tech_test_finish"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    context.user_data[USER_STARTED] = True

    log.info(f"User {context.user_data[USER_ID]} called tech_finish")


def tech_help(update, context):
    update.message.reply_text(strings["tech_test_back"])


def end_tech_viewing(update, context):
    log.info(f"User {context.user_data[USER_ID]} called end_tech_viewing")
    select_exam(update, context)
    return END


def end_tech_test(update, context):
    log.info(f"User {context.user_data[USER_ID]} called end_tech_test")
    start_tech(update, context)
    return END


def start_complex(update, context):
    update.callback_query.answer()
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=strings["complex_start"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called start_complex")
    return VIEWING_COMPLEX


def start_fire2(update, context):
    update.callback_query.answer()
    keyboard = set_keyboard_1(strings["back"], END)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=strings["fire2_start"],
        reply_markup=reply_markup,
        parse_mode="markdown",
    )

    log.info(f"User {context.user_data[USER_ID]} called start_fire2")
    return VIEWING_FIRE2


def main(bot_token):
    updater = Updater(bot_token)

    tech_test_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                tech_test,
                pattern="^" + str(STARTING_TECH) + "$",
            )
        ],
        states={
            STARTING_TECH: [
                CallbackQueryHandler(
                    tech_test_buttons,
                    # pattern=f"^((?!{str(END)}).)*$",
                ),
                MessageHandler(Filters.text & ~Filters.command, tech_help),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                end_tech_test,
                pattern="^" + str(END) + "$",
            ),
            CommandHandler("back", start_tech),
        ],
        map_to_parent={
            VIEWING_TECH: VIEWING_TECH,
            END: VIEWING_TECH,
        },
    )

    tech_handler = [
        tech_test_handler,
        CallbackQueryHandler(
            tech_stats,
            pattern="^" + str(VIEWING_TECH_STATS) + "$",
        ),
        CallbackQueryHandler(
            tech_extra,
            pattern="^" + str(VIEWING_TECH_EXTRA) + "$",
        ),
        CallbackQueryHandler(
            tech_reset,
            pattern="^" + str(RESETTING_TECH) + "$",
        ),
    ]

    tech_view_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_tech,
                pattern="^" + str(VIEWING_TECH) + "$",
            )
        ],
        states={
            VIEWING_TECH: tech_handler,
            VIEWING_TECH_STATS: [
                CallbackQueryHandler(
                    start_tech,
                    pattern="^" + str(END) + "$",
                )
            ],
            VIEWING_TECH_EXTRA: [
                CallbackQueryHandler(
                    start_tech,
                    pattern="^" + str(END) + "$",
                )
            ],
            RESETTING_TECH: [
                CallbackQueryHandler(
                    start_tech,
                    pattern="^" + str(END) + "$",
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                end_tech_viewing,
                pattern="^" + str(END) + "$",
            )
        ],
        map_to_parent={
            END: SELECTING_EXAM,
        },
    )

    exams_handlers = [
        tech_view_handler,
        CallbackQueryHandler(
            start_complex,
            pattern="^" + str(VIEWING_COMPLEX) + "$",
        ),
        CallbackQueryHandler(
            start_fire2,
            pattern="^" + str(VIEWING_FIRE2) + "$",
        ),
    ]

    exam_selection_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                select_exam,
                pattern="^" + str(SELECTING_EXAM) + "$",
            )
        ],
        states={
            SELECTING_EXAM: exams_handlers,
            VIEWING_COMPLEX: [
                CallbackQueryHandler(
                    select_exam,
                    pattern="^" + str(END) + "$",
                )
            ],
            VIEWING_FIRE2: [
                CallbackQueryHandler(
                    select_exam,
                    pattern="^" + str(VIEWING_FIRE2) + "$",
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                end_exam_selecting,
                pattern="^" + str(END) + "$",
            )
        ],
        map_to_parent={
            END: SELECTING_MAIN,
        },
    )

    main_handlers = [
        exam_selection_handler,
        CallbackQueryHandler(
            view_sticker_packs,
            pattern="^" + str(VIEWING_STICKER_PACKS) + "$",
        ),
        CallbackQueryHandler(
            donate,
            pattern="^" + str(DONATING) + "$",
        ),
        CallbackQueryHandler(
            submit_bug,
            pattern="^" + str(SUBMITTING_BUG) + "$",
        ),
        CallbackQueryHandler(
            stop,
            pattern="^" + str(END) + "$",
        ),
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_main)],
        states={
            SELECTING_MAIN: main_handlers,
            VIEWING_STICKER_PACKS: [
                CallbackQueryHandler(
                    start_main,
                    pattern="^" + str(END) + "$",
                )
            ],
            DONATING: [
                CallbackQueryHandler(
                    start_main,
                    pattern="^" + str(END) + "$",
                )
            ],
            SUBMITTING_BUG: [
                CallbackQueryHandler(
                    start_main,
                    pattern="^" + str(END) + "$",
                )
            ],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(BOT_TOKEN)
