from database.database import database_obj as database
from types import MappingProxyType

LEXICON: dict[str, str] = {
    "/start": "Привет! Этот бот поможет вести статистику тренировок.\n"
    "Мне нужны некоторые данные о Вас.\n"
    "Вы готовы ответить на пару вопросов?",
    "enter_name": "Введите полное имя.",
    "error_name": "Имя должно сосоять только из букв.",
    "enter_age": "Введите возраст.",
    "error_old": "Возраст должен состоять только из цифр",
    "enter_gender": "Введите пол.",
    "enter_height": "Введите рост.",
    "error_height": "Рост должен состоять только из цифр.",
    "enter_weight": "Введите вес.",
    "error_weight": "Вес должен состоять только из цифр.",
    "use_btn_pls": "Воспользуйтесь пожалуйста кнопками снизу.",
    "wait": "Если передумаете, просто нажмите кнопку /start.",
    "questionnaire_ready": "Анкета готова!\nТеперь можно начать составлять программы тренировок и тренироваться.",
    "questionnaire_again": "Тогда давайте заполним анкету заново.",
    "menu": "Меню",
    "enter_name_workout": "Введите название тренировки",
    "create_workout_success": "Тренировкка создана",
    "repeat_name_workout": "Тренировка с таким названием уже существует.\nВведите другое название либо удалите тренировку с таким же названием.",
    "select_archive": "Выберите тренировки для архивации",
    "delete": "Выберите тренировки для удаления",
    "dearchive": "Выберите тренировки для восстановления из архива",
    "workout": "Тренировка:",
    "enter_name_exercise": "Введите название упражнения",
    "repeat_name_exercise": "Упражнение с таким названием уже существует.\nВведите другое название.",
    "delete_exercise": "Выберите упражнение для удаления",
}

COMMANDS = MappingProxyType(
    {
        "/start": "🚀 Старт 🚀",
        "/help": "📖 Справка по работе бота 📖",
    }
)

BUTTON = MappingProxyType(
    {
        "yes": "✅ ДА ✅",
        "no": "❌ НЕТ ❌",
        "male": "👨 Мужской 👨",
        "female": "👩 Женский 👩",
    }
)

MAIN_MENU = MappingProxyType(
    {
        "edit_workouts": "⚙️ Редактировать тренировки ⚙️",
    }
)

EDIT_ACTION = MappingProxyType({"ready": "✔️ Готово ✔️"})

EDIT_WORKOUTS = MappingProxyType(
    {
        "create_workout": "➕ Создать ➕",
        "archive": "📥 Архивировать 📥",
        "delete": "🗑️ Удалить 🗑️",
        "dearchive": "📤 Добавить из архива 📤",
        "main_menu": "🏠 Главное меню 🏠",
    }
)

WORKOUT_MENU = MappingProxyType(
    {
        "start": "▶️ Старт ▶️",
        "main_menu": "🏠 Главное меню 🏠",
    }
)

START_WORKOUT = MappingProxyType(
    {
        "new": "🆕 Новое упражнение 🆕",
        "other": "🔄 Другое упражнение 🔄",
        "delete": "🗑️ Удалить строку 🗑️",
        "end": "🏁 Конец тренировки 🏁",
    }
)

DO_EXERCISE = MappingProxyType(
    {
        "finish": "✅ Закончить упражнение ✅",
        "history": "📜 История 📜",
    }
)

OTHER_EXERCISE = MappingProxyType(
    {
        "back": "↩️ Назад ↩️",
    }
)

HISTORY_EXERCISE = MappingProxyType(
    {
        "back": "↩️ Назад ↩️",
    }
)

DELETE_EXERCISE = MappingProxyType(
    {
        "back": "↩️ Назад ↩️",
    }
)


async def weight_workout(workout: int) -> str:
    """Возвращает названия упражнений с весами для тренировки"""
    data = await database.get_weight_workout(workout)
    return "\n".join([f"{i}: {j}" for i, j, _ in data])


async def workout_type_text(workout_type: int) -> str:
    """Возвращает текст для типа транировки"""
    res = await database.get_name_workout_type(workout_type) + "\n\n"
    # получаем id последних тренировок
    ids = await database.get_latest_workout_ids(workout_type)
    ids.reverse()
    for i in ids:
        date = await database.get_date_workout(i)
        weights = await weight_workout(i)
        res += date + "\n" + weights + "\n\n"

    return res


async def workout_end_text(workout: int) -> str:
    """Возвращает текст для окончания тренировки"""
    info = await database.get_info_workout(workout)
    name = await database.get_name_workout_type(info[3])

    res = f"{name}\nПродолжительность - {info[2]} мин\n\n" + await weight_workout(
        workout
    )

    return res


async def history_exercise(exercise_type: int) -> str:
    """Возвращает текст для истории упражнения"""
    data = await database.get_exercise_history(exercise_type)
    res = ""
    for name, date, time, weights in data:
        res += f"{name}. {date} {time} - {weights}\n"
    return res


def create_questionnaire_text(data: dict) -> str:
    """Возвращает текст с анкетой пользователя"""
    return (
        "Вот ваша анкета:\n\n"
        f"Имя - {data['name']}\n"
        f"Возраст - {data['old']}\n"
        f"Пол - {data['gender']}\n"
        f"Рост - {data['height']}\n"
        f"Вес - {data['weight']}\n"
        "\nВсе верно?"
    )
