from telegram import InlineKeyboardButton


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
