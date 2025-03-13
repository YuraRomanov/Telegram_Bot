import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Роли пользователей
masters = [123456789]  # Твой ID как Мастера (позже добавим сюда других мастеров)
workers = []  # Список рабочих

# Состояние для создания задания
class TaskState(StatesGroup):
    detail = State()
    quantity = State()
    deadline = State()

# Команда для мастеров — добавить задание рабочему
@dp.message_handler(commands=['add'], user_id=masters)
async def add_task(message: types.Message):
    await message.answer("Наименование детали:")
    await TaskState.detail.set()

@dp.message_handler(state=TaskState.detail)
async def process_detail(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['detail'] = message.text
    await message.answer("Количество деталей:")
    await TaskState.quantity.set()

@dp.message_handler(state=TaskState.quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity'] = message.text
    await message.answer("Срок выполнения:")
    await TaskState.deadline.set()

@dp.message_handler(state=TaskState.deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['deadline'] = message.text
    
    # Отправляем задание рабочим
    for worker_id in workers:
        await bot.send_message(
            worker_id,
            f"📍 Новое задание:\n🔧 Деталь: {data['detail']}\n📦 Количество: {data['quantity']}\n⏳ Срок: {data['deadline']}"
        )
    await message.answer("✅ Задание отправлено рабочим.")
    await state.finish()

# Подключаем обработчик сообщений
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Привет! Я бот для отслеживания деталей.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
