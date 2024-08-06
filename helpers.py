import string

from datetime import datetime

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

BUTTON_CANCEL = KeyboardButton(text="❌ Скасувати")


def build_year_keyboard() -> ReplyKeyboardMarkup:
    year_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=f"{year}") for year in range(2021, int(datetime.now().year)+1)] + [BUTTON_CANCEL]],
                                        one_time_keyboard=True)
    return year_keyboard


def build_start_keyboard() -> InlineKeyboardMarkup:
    start_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                          [[InlineKeyboardButton(text="⭐ Оцінити", callback_data="rate"),
                                            InlineKeyboardButton(text="🔎 Оцінка", callback_data="avg")]])
    return start_keyboard


def build_admin_keyboard() -> InlineKeyboardMarkup:
    start_keyboard = InlineKeyboardMarkup(inline_keyboard=
                                          [[InlineKeyboardButton(text="⭐ Оцінити", callback_data="rate"),
                                            InlineKeyboardButton(text="🔎 Оцінка", callback_data="avg"),
                                            InlineKeyboardButton(text="Додати/Видалити", callback_data="admin")]])
    return start_keyboard


def build_rate_keyboard() -> ReplyKeyboardMarkup:
    rate_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=f"{i+1}") for i in range(5)],
                                                  [KeyboardButton(text=f"{i+1}") for i in range(5, 10)]],
                                        one_time_keyboard=True)
    return rate_keyboard


def build_book_keyboard(books: list[str]) -> ReplyKeyboardMarkup:
    book_keys = [KeyboardButton(text=f"{book}") for book in books]
    if len(books) <= 3:
        book_markup = [book_keys]
    else:
        book_markup = [book_keys[i:i + 3] for i in range(0, len(book_keys), 3)]
    book_markup.append([BUTTON_CANCEL])
    return ReplyKeyboardMarkup(keyboard=book_markup, one_time_keyboard=True)


def strip_punctuation(text: str) -> str:
    return ''.join([char for char in text if char not in set(string.punctuation)]).lower()
