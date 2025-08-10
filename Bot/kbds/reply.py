from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


del_kb = ReplyKeyboardRemove()

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Начать анализ')],
        [KeyboardButton(text='Помощь')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Нажмите на кнопку'
)

help_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Назад')],
    ],
    resize_keyboard=True,
    input_field_placeholder='...'
)


analiz_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='WinOrient')],
        [KeyboardButton(text='SportOrg')],
        [KeyboardButton(text='SFR')],
        [KeyboardButton(text='Назад')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Нажмите на кнопку'
)

func_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Сравнить группу спортсменов (DEMO, только WinOrient)')],
        [KeyboardButton(text='Проигрыш по перегонам')],
        [KeyboardButton(text='Топ10 на каждом перегоне в группе')],
        [KeyboardButton(text='Топ10 на каждом перегоне среди всех участников')],
        [KeyboardButton(text='Топ10 на конкретном перегоне')],
        [KeyboardButton(text='Назад')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Нажмите на кнопку'
)

types_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Заданное направление')],
        [KeyboardButton(text='Общий старт')],
        [KeyboardButton(text='Эстафета')],
        [KeyboardButton(text='Выбор')],
        [KeyboardButton(text='Назад')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Нажмите на кнопку'
)


def make_group_keyboard(groups: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=group)] for group in groups]
    keyboard.append([KeyboardButton(text='Назад')])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)