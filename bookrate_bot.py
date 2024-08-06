from __future__ import annotations

import logging
from datetime import datetime

from database import Database
from helpers import (
    build_rate_keyboard,
    build_start_keyboard,
    build_book_keyboard,
    build_year_keyboard,
    build_admin_keyboard,
    BUTTON_CANCEL
)

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import After, Scene, SceneRegistry, on
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)

db = Database()

with open("token.txt", "r") as token:
    TOKEN = token.read()


class CancellableScene(Scene):
    @on.message(F.text.casefold() == BUTTON_CANCEL.text.casefold(), after=After.exit())
    async def handle_cancel(self, message: Message):
        await message.answer("Скасовано.", reply_markup=ReplyKeyboardRemove())


class AddDeleteScene(CancellableScene, state="admin"):
    """
    У цій сцені обробляється процес додавання або видалення книг із бази даних для адміністратора
    Крок №0 - Запитуємо, що хотіли б зробити - додати або видалити
    Крок №1 - Запитуємо назву книги
    Крок №2 - Запитуємо рік прочитання книги
    Крок №3 - Додаємо або видаляємо книгу та повідомляємо про успішну дію
    """
    pass


class RateScene(CancellableScene, state="rate"):
    """
    У цій сцені обробляється процес виведення середньої оцінки книги
    Крок №0 - Запитуємо рік, в якому книжковий клуб читав книгу
    Крок №1 - Запитуємо назву книги
    Крок №2 - Запитуємо яку оцінку заслуговує книгу, на думку користувача
    Крок №3 - Зберігаємо оцінку
    """
    @on.callback_query.enter()
    async def on_enter_callback(self, callback_query: CallbackQuery, state: FSMContext):
        await callback_query.message.answer("Коли ми читали цю книгу?",
                                            reply_markup=build_year_keyboard(),
                                            one_time_keyboard=True)
        data = await state.get_data()
        await state.update_data(step=data.get('step')+1)
        logging.log(level=logging.DEBUG, msg=f"State: {await state.get_state()}")

    @on.message(F.text)
    async def on_message(self, message: Message, state: FSMContext):
        data = await state.get_data()
        current_step = data.get('step')

        try:
            if current_step == 1:  # Обираємо книгу
                if int(message.text) > 2020:
                    await state.update_data(step=data.get('step') + 1)
                    await message.answer("Яку книгу ви б хотіли оцінити?",
                                         reply_markup=build_book_keyboard(db.get_books_on_year(int(message.text))))
                else:
                    await message.answer(f"Введіть рік між 2021 та {datetime.now().year}")
            elif current_step == 2:  # Запитуємо, яку оцінку поставити
                if message.text in db.get_all_books():
                    await state.update_data(step=data.get('step') + 1)
                    await state.update_data(book=message.text)
                    await message.answer("Яку оцінку, на Вашу думку, заслуговує ця книга?",
                                         reply_markup=build_rate_keyboard())
                else:
                    await state.update_data(step=0)
                    await message.answer("Книгу не знайдено.")
                    await self.wizard.exit()
            elif current_step == 3:  # Зберігаємо оцінку
                if int(message.text) in range(1, 11):
                    await state.update_data(step=0)
                    data = await state.get_data()
                    db.set_rate(int(message.from_user.id), data.get('book'), message.text)
                    await message.answer("Дякую! Оцінку збережено!")
                    await self.wizard.exit()
                else:
                    raise ValueError("Введіть цифру між 1 та 10.")
        except ValueError:
            await state.update_data(step=0)
            await message.answer("Введіть цифру між 1 та 10.")
            await self.wizard.exit()


class AvgScene(CancellableScene, state="avg"):
    """
    У цій сцені обробляється процес виведення середньої оцінки книги
    Крок №0 - Запитуємо рік, в якому книжковий клуб читав книгу
    Крок №1 - Запитуємо назву книги
    Крок №2 - Виводимо середню оцінку книги
    """
    @on.callback_query.enter()
    async def on_enter_callback(self, callback_query: CallbackQuery, state: FSMContext):
        # Запитуємо рік в якому читацький клуб прочитав книгу
        await callback_query.message.answer("Коли ми читали цю книгу?",
                                            reply_markup=build_year_keyboard(),
                                            one_time_keyboard=True)
        data = await state.get_data()
        await state.update_data(step=data.get('step')+1)
        logging.log(level=logging.DEBUG, msg=f"State: {await state.get_state()}")

    @on.message(F.text)
    async def on_message(self, message: Message, state: FSMContext):
        data = await state.get_data()
        current_step = data.get('step')
        try:
            if current_step == 1:  # Обираємо книгу
                if int(message.text) > 2020:
                    await state.update_data(step=data.get('step') + 1)
                    await message.answer("Оцінку якої книги Ви б хотіли переглянути?",
                                         reply_markup=build_book_keyboard(db.get_books_on_year(int(message.text))))
                else:
                    await message.answer(f"Введіть рік між 2021 та {datetime.now().year}")
            elif current_step == 2:  # Виводимо оцінку
                if message.text in db.get_all_books():
                    await state.update_data(step=0)
                    await message.answer(f"Середня оцінка книги {message.text} - {int(db.get_rate(message.text))}.")
                    await self.wizard.exit()
                else:
                    await state.update_data(step=0)
                    await message.answer("Книгу не знайдено.")
                    await self.wizard.exit()
        except TypeError:
            await state.update_data(step=0)
            await message.answer("Ще немає оцінок")
            await self.wizard.exit()


class DefaultScene(
    Scene,
    reset_data_on_enter=True,  # Reset state data
    reset_history_on_enter=True,  # Reset history
    callback_query_without_state=True,  # Handle callback queries even if user in any scene
):

    @on.message.enter()
    @on.message(Command("start"))
    async def default_handler(self, message: Message, state: FSMContext):
        await state.update_data(step=0)
        await message.answer(
            f"""Привіт {message.from_user.first_name}!
              \nЯ допоможу тобі оцінити книги прочитані читацьким клубом Intellias.""",
            reply_markup=build_start_keyboard()
        )

    @on.callback_query(F.data == "rate", after=After.goto(RateScene))
    async def rate_callback(self, callback_query: CallbackQuery):
        await callback_query.answer(cache_time=0)
        await callback_query.message.delete_reply_markup()

    @on.callback_query(F.data == "avg", after=After.goto(AvgScene))
    async def avg_callback(self, callback_query: CallbackQuery):
        await callback_query.answer(cache_time=0)
        await callback_query.message.delete_reply_markup()

    @on.callback_query(F.data == "admin", after=After.goto(AddDeleteScene))
    async def add_delete_callback(self, callback_query: CallbackQuery):
        await callback_query.answer(cache_time=0)
        await callback_query.message.delete_reply_markup()


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()

    registry = SceneRegistry(dispatcher)
    registry.add(
        DefaultScene,
        AvgScene,
        RateScene,
        AddDeleteScene,
    )

    return dispatcher


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dp = create_dispatcher()
    bot = Bot(TOKEN)
    dp.run_polling(bot)
