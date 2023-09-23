import logging
import random
from bot import SHEET_KEY, SHEET_NAME_TECH, SHEET_NAME_USERS, TOKEN, PARSE_MODE, strings
from bot.helper.google_sheets import get_questions
from bot.helper.keyboards import set_keyboard_small, set_keyboard_wide
from bot import application, strings
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

QUESTION = range(1)


async def start(update, context):
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

    await update.message.reply_text(
        text=strings["quiz_start"].format(number=len(context.user_data["questions"])),
        parse_mode=PARSE_MODE,
    )

    return await form_question(update, context)


async def form_question(update, context):
    logger.info(
        f"User {context.user_data['username']} has {len(context.user_data['questions'])} unanswered questions"
    )

    if len(context.user_data["questions"]) == 0:
        await update.message.reply_text(
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
        # print("photo")
        with open(
            "bot/config/images/" + context.user_data["question_photo"] + ".png",
            "rb",
        ) as image:
            await update.message.reply_photo(
                photo=image,
                caption=context.user_data["question"],
                reply_markup=reply_markup,
            )
    else:
        await update.message.reply_text(
            context.user_data["question"], reply_markup=reply_markup
        )
    return QUESTION


async def answer_button(update, context):
    query = update.callback_query
    await query.answer()

    edit_type, message_type = (
        ("edit_message_caption", "caption")
        if context.user_data["question_photo"]
        else ("edit_message_text", "text")
    )

    answer = (
        "right_answer" if query.data == context.user_data["answer"] else "wrong_answer"
    )

    await getattr(query, edit_type)(
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

    return await form_question(query, context)


async def cancel(update, context):
    await update.message.reply_text(
        text=strings["quiz_finish"].format(
            right_count=context.user_data["right_count"],
            wrong_count=context.user_data["wrong_count"],
        ),
        parse_mode=PARSE_MODE,
    )
    logger.info(f"User {update.message.from_user['username']} called cancel")
    return ConversationHandler.END


async def false_start(update, context):
    await update.message.reply_text(strings["false_start"], parse_mode=PARSE_MODE)
    logger.info(f"User {update.message.from_user['username']} called false_start")


async def false_cancel(update, context):
    await update.message.reply_text(strings["false_cancel"], parse_mode=PARSE_MODE)
    logger.info(f"User {update.message.from_user['username']} called false_cancel")


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    allow_reentry=False,
    states={QUESTION: [CallbackQueryHandler(answer_button)]},
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)

application.add_handler(CommandHandler("start", false_start))
application.add_handler(CommandHandler("cancel", false_cancel))
