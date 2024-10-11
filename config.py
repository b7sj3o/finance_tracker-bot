import logging
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from aiogram import BaseMiddleware
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

logs_dir = BASE_DIR / "logs"
if not logs_dir.exists():
    logs_dir.mkdir(parents=True)

logger = logging.getLogger("aiogram")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(logs_dir / "bot.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if event.message:
            logger.info(
                f"Received message from {event.message.from_user.username}: {event.message.text}"
            )
        else:
            logger.info(f"Received update: {event}")
        return await handler(event, data)


bot = Bot(
    token=os.getenv("API_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.update.middleware(LoggingMiddleware())
router = Router()
API_BASE_URL = "https://127.0.0.1:8000/api/"
API_ENDPOINT_EXPENSE = "expense/"
API_ENDPOINT_INCOME = "income/"
MAX_AMOUNT = 10000000


class Expense(StatesGroup):
    waiting_for_expense_details = State()
    waiting_for_expense_id = State()
    waiting_for_delete_id = State()
    waiting_for_update_details = State()


class Income(StatesGroup):
    waiting_for_income_details = State()
    waiting_for_income_id = State()
    waiting_for_delete_id = State()
    waiting_for_update_details = State()
