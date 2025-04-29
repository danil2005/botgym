from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def other_messages(message: Message):
    """Команда отвечает сообщения, которые не попали не в один обработчик"""
    await message.answer("Что-то пошло не так(\nВведите команду /start")
