from config import dp
from db import db_session, Finance, User
from .routes import router, add_expense

def setup_handlers():
    dp.include_router(router)