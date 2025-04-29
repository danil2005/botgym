from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.database import database_obj as database
from lexicon import lexicon
from aiogram import Bot
from aiogram.types import BotCommand


def create_keyboard(*names: str) -> ReplyKeyboardMarkup:
    """Возвращает объект кнопок по списку"""
    buttons = [KeyboardButton(text=i) for i in names]
    return ReplyKeyboardMarkup(
        keyboard=[buttons], resize_keyboard=True, one_time_keyboard=True
    )


keyboard_no_yes = create_keyboard(lexicon.BUTTON["yes"], lexicon.BUTTON["no"])
keyboard_gender = create_keyboard(lexicon.BUTTON["male"], lexicon.BUTTON["female"])


def create_inline_keyboard(data: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок"""
    buttons = [InlineKeyboardButton(callback_data=str(d), text=t) for d, t in data]
    ikb_builder = InlineKeyboardBuilder()
    ikb_builder.row(*buttons, width=1)
    return ikb_builder.as_markup()


async def inline_kb_main_menu(user_id: int) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для основного меню"""
    workouts = await database.get_workout_types(user_id, "active")
    workouts = [(str(i), j) for i, j in workouts]
    data = workouts + list(lexicon.MAIN_MENU.items())
    return create_inline_keyboard(data)


def inline_kb_edit_workouts() -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню редактирования типов тренировок"""
    return create_inline_keyboard(lexicon.EDIT_WORKOUTS.items())


async def inline_kb_archive_workouts(user_id: int) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню архивации типов тренировок"""
    workouts = await database.get_workout_types(user_id, "active")
    workouts = [(str(i), j) for i, j in workouts]
    data = workouts + list(lexicon.EDIT_ACTION.items())
    return create_inline_keyboard(data)


async def inline_kb_delete_workouts(user_id: int) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню удаления типов тренировок"""
    workouts = await database.get_workout_types(user_id)
    workouts = [(str(i), j) for i, j in workouts]
    data = workouts + list(lexicon.EDIT_ACTION.items())
    return create_inline_keyboard(data)


async def inline_kb_dearchive_workouts(user_id: int) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню деархивации тренировок"""
    workouts = await database.get_workout_types(user_id, "deactive")
    workouts = [(str(i), j) for i, j in workouts]
    data = workouts + list(lexicon.EDIT_ACTION.items())
    return create_inline_keyboard(data)


def inline_kb_menu_workouts() -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для основного меню"""
    data = list(lexicon.WORKOUT_MENU.items())
    return create_inline_keyboard(data)


async def inline_kb_do_workout(
    workout_type: int, completed_exercises: list[int] | None = None
) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню выполнения тренировки"""
    exercises = list(await database.get_workout_exercises(workout_type))
    if completed_exercises is not None:
        exercises = [i for i in exercises if i[0] not in completed_exercises]
    data = exercises + list(lexicon.START_WORKOUT.items())
    return create_inline_keyboard(data)


def inline_kb_do_exercise() -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню выполнения упражнения"""
    data = list(lexicon.DO_EXERCISE.items())
    return create_inline_keyboard(data)


async def inline_kb_other_exercise(
    chat_id: int, workout_type: int, completed_exercises: list[int]
) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню выбора другого упражнения, которое не выполнялось в прошлую тренировку"""
    exercises = await database.get_all_exercise_types(chat_id)
    current_exercises = await database.get_workout_exercises(workout_type)
    current_exercises = [i[0] for i in current_exercises] + completed_exercises
    exercises = [i for i in exercises if i[0] not in current_exercises]
    return create_inline_keyboard(exercises + list(lexicon.OTHER_EXERCISE.items()))


def inline_kb_history_exercise() -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню истории упражнения"""
    data = list(lexicon.HISTORY_EXERCISE.items())
    return create_inline_keyboard(data)


async def inline_kb_delete_exercise(workout: int) -> InlineKeyboardMarkup:
    """Возвращает объект инлайн кнопок для меню удаления упражнений"""
    exercises = await database.get_weight_workout(workout)
    data = [(str(k), f"{i}: {j}") for i, j, k in exercises]
    return create_inline_keyboard(data + list(lexicon.DELETE_EXERCISE.items()))


async def set_main_menu(bot: Bot) -> None:
    """Функция для настройки кнопки Menu бота"""
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in lexicon.COMMANDS.items()
    ]
    await bot.set_my_commands(main_menu_commands)
