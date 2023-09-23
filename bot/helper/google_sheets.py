import gspread
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
