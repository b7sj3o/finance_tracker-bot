from .config import dp, bot, API_BASE_URL, API_ENDPOINT_EXPENSE, API_ENDPOINT_INCOME, MAX_AMOUNT
from .utils import (
    generate_csv_report,
    get_all_users,
    generate_xlsx_report,
)
from .db.models import db_session, User, Finance
from .handlers import setup_handlers

setup_handlers()

if __name__ == "__main__":
    dp.run_polling(bot)
