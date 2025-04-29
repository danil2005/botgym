from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from filters.fsm import FSMFillForm

from lexicon import lexicon
from lexicon.lexicon import LEXICON
from keyboards import keyboards
from database.database import database_obj as database

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    """Обработка команды старт, в любом состоянии fsm, кроме дефолтного"""
    await message.answer(
        LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(message.chat.id),
    )
    await state.clear()
    await state.set_state(FSMFillForm.main_menu)


@router.callback_query(StateFilter(FSMFillForm.main_menu), F.data == "edit_workouts")
async def process_edite_workouts(callback: CallbackQuery, state: FSMContext):
    """Обработка инлайн-кнопки рдектировать типы тренировок"""
    await callback.answer()
    await callback.message.edit_text(
        text=lexicon.MAIN_MENU["edit_workouts"],
        reply_markup=keyboards.inline_kb_edit_workouts(),
    )
    await state.set_state(FSMFillForm.edite_workouts)


@router.callback_query(StateFilter(FSMFillForm.edite_workouts), F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    """Обработка инлайн-кнопки вернуться в главное меню"""
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(callback.message.chat.id),
    )
    await state.set_state(FSMFillForm.main_menu)


@router.callback_query(
    StateFilter(FSMFillForm.edite_workouts), F.data == "create_workout"
)
async def process_create_workout(callback: CallbackQuery, state: FSMContext):
    """Обработка инлайн-кнопки создать новый тип тренировки"""
    await callback.answer()
    await callback.message.delete()
    sent_message = await callback.message.answer(LEXICON["enter_name_workout"])
    await state.set_state(FSMFillForm.enter_name_workout)
    await state.update_data(
        temp_messages=[
            sent_message.message_id,
        ]
    )


@router.message(StateFilter(FSMFillForm.enter_name_workout))
async def process_enter_name_workout(message: Message, state: FSMContext):
    """Обработка ввода названия нового типа тренировки"""
    data = await state.get_data()
    data["temp_messages"].append(message.message_id)

    if await database.add_new_workout_type(message.chat.id, message.text):
        for i in data["temp_messages"]:
            await message.bot.delete_message(message.chat.id, i)

        await message.answer(
            LEXICON["menu"],
            reply_markup=await keyboards.inline_kb_main_menu(message.chat.id),
        )
        await state.set_state(FSMFillForm.main_menu)
    else:
        sent_message = await message.answer(LEXICON["repeat_name_workout"])
        data["temp_messages"].append(sent_message.message_id)
        await state.update_data(temp_messages=data["temp_messages"])


@router.callback_query(StateFilter(FSMFillForm.edite_workouts), F.data == "archive")
async def process_archive_workout(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки для перехода в меню архивирования типов тренировок"""
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["select_archive"],
        reply_markup=await keyboards.inline_kb_archive_workouts(
            callback.message.chat.id
        ),
    )
    await state.set_state(FSMFillForm.archive)


@router.callback_query(StateFilter(FSMFillForm.archive), F.data.isdigit())
async def process_archive_select(callback: CallbackQuery):
    """Обработка выбора конкретного типа тренировки для архивирования"""
    await database.set_active_workout_type(int(callback.data), False)
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["select_archive"],
        reply_markup=await keyboards.inline_kb_archive_workouts(
            callback.message.chat.id
        ),
    )


@router.callback_query(StateFilter(FSMFillForm.archive), F.data == "ready")
async def process_archive_ready(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню из меню архивирования типов тренировок"""
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(callback.message.chat.id),
    )
    await state.set_state(FSMFillForm.main_menu)


@router.callback_query(StateFilter(FSMFillForm.edite_workouts), F.data == "delete")
async def process_delete_workout(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки для перехода в меню удаления типов тренировок"""
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["delete"],
        reply_markup=await keyboards.inline_kb_delete_workouts(
            callback.message.chat.id
        ),
    )
    await state.set_state(FSMFillForm.delete)


@router.callback_query(StateFilter(FSMFillForm.delete), F.data.isdigit())
async def process_delete_select(callback: CallbackQuery):
    """Обработка кнопки выбора типа тренировки для удаления"""
    await database.delete_workout_type(int(callback.data))
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["delete"],
        reply_markup=await keyboards.inline_kb_delete_workouts(
            callback.message.chat.id
        ),
    )


@router.callback_query(StateFilter(FSMFillForm.delete), F.data == "ready")
async def process_delete_ready(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню из меню удаления типов тренировок"""
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(callback.message.chat.id),
    )
    await state.set_state(FSMFillForm.main_menu)


@router.callback_query(StateFilter(FSMFillForm.edite_workouts), F.data == "dearchive")
async def process_dearchive_workout(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки для перехода в меню восстановления из архива типов тренировок"""
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["dearchive"],
        reply_markup=await keyboards.inline_kb_dearchive_workouts(
            callback.message.chat.id
        ),
    )
    await state.set_state(FSMFillForm.dearchive)


@router.callback_query(StateFilter(FSMFillForm.dearchive), F.data.isdigit())
async def process_dearchive_select(callback: CallbackQuery):
    """Обработка кнопки выбора типа тренировки для восстановления из архива"""
    await database.set_active_workout_type(int(callback.data), True)
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON["dearchive"],
        reply_markup=await keyboards.inline_kb_dearchive_workouts(
            callback.message.chat.id
        ),
    )


@router.callback_query(StateFilter(FSMFillForm.dearchive), F.data == "ready")
async def process_dearchive_ready(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню из меню восстановления из архива типов тренировок"""
    await callback.answer()
    await callback.message.edit_text(
        LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(callback.message.chat.id),
    )
    await state.set_state(FSMFillForm.main_menu)
