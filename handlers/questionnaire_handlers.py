from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from filters.fsm import FSMFillForm

from lexicon import lexicon
from keyboards import keyboards
from database.database import database_obj as database

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    """Обработка кнопки /start"""
    await message.answer(
        lexicon.LEXICON[message.text], reply_markup=keyboards.keyboard_no_yes
    )
    await state.set_state(FSMFillForm.is_ready_questionnaire)


@router.message(
    StateFilter(FSMFillForm.is_ready_questionnaire), F.text == lexicon.BUTTON["yes"]
)
async def process_yes_questionnaire(message: Message, state: FSMContext):
    """Обработка положительного ответа на предложение заполнить анкету"""
    await message.answer(
        lexicon.LEXICON["enter_name"], reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FSMFillForm.fill_name)
    await state.update_data(chat_id=message.chat.id)


@router.message(
    StateFilter(FSMFillForm.is_ready_questionnaire), F.text == lexicon.BUTTON["no"]
)
async def process_no_questionnaire(message: Message, state: FSMContext):
    """Обработка отрицательного ответа на предложение заполнить анкету"""
    await message.answer(lexicon.LEXICON["wait"], reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(StateFilter(FSMFillForm.is_ready_questionnaire))
async def process_other_questionnaire(message: Message):
    """Обработка ответа на предложение заполнить анкету, если пользователь не воспользовался кнопками"""
    await message.answer(
        lexicon.LEXICON["use_btn_pls"], reply_markup=keyboards.keyboard_no_yes
    )


@router.message(
    StateFilter(FSMFillForm.fill_name), lambda x: all(map(str.isalpha, x.text.split()))
)
async def process_name(message: Message, state: FSMContext):
    """Обработка корректно введенного имени"""
    await message.answer(lexicon.LEXICON["enter_age"])
    await state.update_data(name=message.text)
    await state.set_state(FSMFillForm.fill_age)


@router.message(StateFilter(FSMFillForm.fill_name))
async def process_name_error(message: Message):
    """Обработка некорректно введенного имени"""
    await message.answer(lexicon.LEXICON["error_name"])


@router.message(StateFilter(FSMFillForm.fill_age), F.text.isdigit())
async def process_old(message: Message, state: FSMContext):
    """Обработка корректно введенного возраста"""
    await message.answer(
        lexicon.LEXICON["enter_gender"], reply_markup=keyboards.keyboard_gender
    )
    await state.update_data(old=int(message.text))
    await state.set_state(FSMFillForm.fill_gender)


@router.message(StateFilter(FSMFillForm.fill_age))
async def process_old_error(message: Message):
    """Обработка некорректно введенного возраста"""
    await message.answer(lexicon.LEXICON["error_old"])


@router.message(
    StateFilter(FSMFillForm.fill_gender),
    F.text.in_([lexicon.BUTTON["male"], lexicon.BUTTON["female"]]),
)
async def process_gender(message: Message, state: FSMContext):
    """Обработка корректно введенного пола"""
    await message.answer(
        lexicon.LEXICON["enter_height"], reply_markup=ReplyKeyboardRemove()
    )
    await state.update_data(
        gender=message.text.strip(
            lexicon.BUTTON["male"][0] + lexicon.BUTTON["female"][0]
        )
    )
    await state.set_state(FSMFillForm.fill_height)


@router.message(StateFilter(FSMFillForm.fill_gender))
async def process_gender_error(message: Message):
    """Обработка некорректно введенного пола"""
    await message.answer(
        lexicon.LEXICON["use_btn_pls"], reply_markup=keyboards.keyboard_gender
    )


@router.message(StateFilter(FSMFillForm.fill_height), F.text.isdigit())
async def process_height(message: Message, state: FSMContext):
    """Обработка корректно введенного роста"""
    await message.answer(lexicon.LEXICON["enter_weight"])
    await state.update_data(height=int(message.text))
    await state.set_state(FSMFillForm.fill_weight)


@router.message(StateFilter(FSMFillForm.fill_height))
async def process_height_error(message: Message):
    """Обработка некорректно введенного роста"""
    await message.answer(lexicon.LEXICON["error_height"])


@router.message(StateFilter(FSMFillForm.fill_weight), F.text.isdigit())
async def process_weight(message: Message, state: FSMContext):
    """Обработка корректно введенного веса"""
    await state.update_data(weight=int(message.text))
    await message.answer(
        lexicon.create_questionnaire_text(await state.get_data()),
        reply_markup=keyboards.keyboard_no_yes,
    )
    await state.set_state(FSMFillForm.is_correct_questionnaire)


@router.message(StateFilter(FSMFillForm.fill_weight))
async def process_weight_error(message: Message):
    """Обработка некорректно введенного веса"""
    await message.answer(lexicon.LEXICON["error_weight"])


@router.message(
    StateFilter(FSMFillForm.is_correct_questionnaire), F.text == lexicon.BUTTON["yes"]
)
async def process_yes_correct_que(message: Message, state: FSMContext):
    """Обработка положительного ответа на вопрос о корректности анкеты"""
    await message.answer(
        lexicon.LEXICON["questionnaire_ready"], reply_markup=ReplyKeyboardRemove()
    )
    await database.add_questionnaire(await state.get_data())
    await state.clear()
    await state.set_state(FSMFillForm.main_menu)
    await message.answer(
        lexicon.LEXICON["menu"],
        reply_markup=await keyboards.inline_kb_main_menu(message.chat.id),
    )


@router.message(
    StateFilter(FSMFillForm.is_correct_questionnaire), F.text == lexicon.BUTTON["no"]
)
async def process_no_correct_que(message: Message, state: FSMContext):
    """Обработка отрицательного ответа на вопрос о корректности анкеты"""
    await message.answer(
        lexicon.LEXICON["questionnaire_again"], reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(lexicon.LEXICON["enter_name"])
    await state.clear()
    await state.update_data(chat_id=message.chat.id)
    await state.set_state(FSMFillForm.fill_name)


@router.message(StateFilter(FSMFillForm.is_correct_questionnaire))
async def process_error_correct_que(message: Message):
    """Обработка ответа на предложение заполнить анкету, если пользователь не воспользовался кнопками"""
    await message.answer(
        lexicon.LEXICON["use_btn_pls"], reply_markup=keyboards.keyboard_no_yes
    )
