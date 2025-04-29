from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from filters.fsm import FSMFillForm

from lexicon.lexicon import LEXICON
from lexicon import lexicon
from keyboards import keyboards
from database.database import database_obj as database

router = Router()


@router.callback_query(StateFilter(FSMFillForm.main_menu), F.data.isdigit())
async def process_menu_workout(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки перехода в меню типа тренировки"""
    await state.update_data(workout_type=int(callback.data))
    await callback.answer()
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(callback.data),
        reply_markup=keyboards.inline_kb_menu_workouts(),
    )
    await state.set_state(FSMFillForm.menu_workout)


@router.callback_query(StateFilter(FSMFillForm.menu_workout), F.data == "main_menu")
async def process_back_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню из меню типа тренировки"""
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(callback.message.chat.id),
    )
    await state.clear()
    await state.set_state(FSMFillForm.main_menu)


@router.callback_query(StateFilter(FSMFillForm.menu_workout), F.data == "start")
async def process_do_workout(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки старта тренировки"""
    data = await state.get_data()
    id_workout = await database.start_workout(
        callback.message.chat.id, data["workout_type"]
    )
    await state.update_data(
        workout=id_workout,
        completed_exercises=[],
        message_id=callback.message.message_id,
    )
    await callback.answer()
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=await keyboards.inline_kb_do_workout(data["workout_type"]),
    )
    await state.set_state(FSMFillForm.do_workout)


@router.callback_query(StateFilter(FSMFillForm.do_workout), F.data.isdigit())
async def process_select_exercise(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки для выбора упражения, которое пользователь выполняет"""
    data = await state.get_data()
    id_exercise = await database.start_exercise(int(callback.data), data["workout"])
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=keyboards.inline_kb_do_exercise(),
    )
    await state.set_state(FSMFillForm.do_exercise)
    data["completed_exercises"].append(int(callback.data))
    await state.update_data(
        exercise_type=int(callback.data),
        exercise=id_exercise,
        completed_exercises=data["completed_exercises"],
    )


@router.callback_query(StateFilter(FSMFillForm.do_workout), F.data == "new")
async def process_new_exercise(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки создания нового типа упрежнения"""
    await callback.answer()
    sent_message = await callback.message.answer(LEXICON["enter_name_exercise"])
    await state.set_state(FSMFillForm.enter_name_exercise)
    await state.update_data(
        temp_messages=[
            sent_message.message_id,
        ]
    )


@router.message(StateFilter(FSMFillForm.enter_name_exercise))
async def process_enter_name_exercise(message: Message, state: FSMContext):
    """Обработка введенного названия упражнения"""
    id_exercise_type = await database.add_new_exercise_type(
        message.chat.id, message.text
    )
    data = await state.get_data()
    data["temp_messages"].append(message.message_id)

    if id_exercise_type:
        for i in data["temp_messages"]:
            await message.bot.delete_message(message.chat.id, i)
        data["completed_exercises"].append(id_exercise_type)
        id_exercise = await database.start_exercise(id_exercise_type, data["workout"])
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data["message_id"],
            text=await lexicon.workout_type_text(data["workout_type"]),
            reply_markup=keyboards.inline_kb_do_exercise(),
        )
        await state.set_state(FSMFillForm.do_exercise)
        await state.update_data(
            exercise_type=int(id_exercise_type),
            exercise=id_exercise,
            completed_exercises=data["completed_exercises"],
        )
    else:
        sent_message = await message.answer(LEXICON["repeat_name_exercise"])
        data["temp_messages"].append(sent_message.message_id)
        await state.update_data(temp_messages=data["temp_messages"])


@router.callback_query(StateFilter(FSMFillForm.do_workout), F.data == "other")
async def process_other_exercise(callback: CallbackQuery, state: FSMContext):
    """Переход в меню для выбора упражнения, которое не выполнялось на прошлой тренировке"""
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=await keyboards.inline_kb_other_exercise(
            callback.message.chat.id, data["workout_type"], data["completed_exercises"]
        ),
    )
    await state.set_state(FSMFillForm.do_workout)


@router.callback_query(StateFilter(FSMFillForm.do_workout), F.data == "back")
async def process_back(callback: CallbackQuery, state: FSMContext):
    """Вернуться из меню для выбора упражнения, которое не выполнялось на прошлой тренировке"""
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=await keyboards.inline_kb_do_workout(
            data["workout_type"], data["completed_exercises"]
        ),
    )


@router.callback_query(StateFilter(FSMFillForm.do_workout), F.data == "delete")
async def process_delete_exercise(callback: CallbackQuery, state: FSMContext):
    """Переход в меню для удаления выполненных упражнений"""
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["delete_exercise"],
        reply_markup=await keyboards.inline_kb_delete_exercise(data["workout"]),
    )
    await state.set_state(FSMFillForm.delete_exercise)


@router.callback_query(StateFilter(FSMFillForm.delete_exercise), F.data.isdigit())
async def process_select_exercise_for_del(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора упражнения для удаления"""
    exerecise_del = await database.delete_exercise(int(callback.data))
    data = await state.get_data()
    data["completed_exercises"].remove(exerecise_del)
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["delete_exercise"],
        reply_markup=await keyboards.inline_kb_delete_exercise(data["workout"]),
    )
    await state.update_data(completed_exercises=data["completed_exercises"])


@router.callback_query(StateFilter(FSMFillForm.delete_exercise), F.data == "back")
async def process_back_delete_exercise(callback: CallbackQuery, state: FSMContext):
    """Вернуться из меню для удаления упражнений"""
    await callback.answer()
    data = await state.get_data()
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=await keyboards.inline_kb_do_workout(
            data["workout_type"], data["completed_exercises"]
        ),
    )
    await state.set_state(FSMFillForm.do_workout)


@router.message(StateFilter(FSMFillForm.do_exercise))
async def process_do_exercise(message: Message, state: FSMContext):
    """Обработка веса подхода упражнения, введенного пользователем"""
    data = await state.get_data()
    await database.update_exercise(data["exercise"], message.text)
    await message.bot.delete_message(message.chat.id, message.message_id)
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["message_id"],
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=keyboards.inline_kb_do_exercise(),
    )


@router.callback_query(StateFilter(FSMFillForm.do_exercise), F.data == "finish")
async def process_end_exercise(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки окончания упражнения"""
    await callback.answer()
    data = await state.get_data()
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=await keyboards.inline_kb_do_workout(
            data["workout_type"], data["completed_exercises"]
        ),
    )
    await state.set_state(FSMFillForm.do_workout)


@router.callback_query(StateFilter(FSMFillForm.do_exercise), F.data == "history")
async def process_history_exercise(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки для вывода истории упражнения"""
    await callback.answer()
    data = await state.get_data()
    await callback.message.edit_text(
        text=await lexicon.history_exercise(data["exercise_type"]),
        reply_markup=keyboards.inline_kb_history_exercise(),
    )
    await state.set_state(FSMFillForm.history_exercise)


@router.callback_query(StateFilter(FSMFillForm.history_exercise), F.data == "back")
async def process_back_history_exercise(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки для возврата из истории упражнения"""
    await callback.answer()
    data = await state.get_data()
    await callback.message.edit_text(
        text=await lexicon.workout_type_text(data["workout_type"]),
        reply_markup=keyboards.inline_kb_do_exercise(),
    )
    await state.set_state(FSMFillForm.do_exercise)


@router.callback_query(StateFilter(FSMFillForm.do_workout), F.data == "end")
async def process_end_workout(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки для окончания тренировки"""
    data = await state.get_data()
    await callback.answer()
    await database.end_workout(data["workout"])
    await callback.message.delete()
    await callback.message.answer(await lexicon.workout_end_text(data["workout"]))
    await callback.message.answer(
        LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(callback.message.chat.id),
    )
    await state.clear()
    await state.set_state(FSMFillForm.main_menu)
