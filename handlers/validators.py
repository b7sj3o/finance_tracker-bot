"""
This module contains validation functions for the finance tracker bot.
"""

from sqlalchemy.sql import text
from db import db_session


async def validate_amount_description(text: str):
    """
    Validates if the given text contains both amount and description.

    Args:
        text (str): Input string with amount and description.

    Returns:
        tuple: (amount, description) if valid, else (None, error message).
    """
    parts = text.split(" ", 1)
    if len(parts) != 2:
        return None, "Invalid format. Please provide both amount and description."

    amount_str, description = parts
    try:
        amount = float(amount_str)
        return amount, description
    except ValueError:
        return None, "Invalid amount. Please enter a numeric value."


async def validate_user_exists(username: str):
    """
    Validates if the user exists in the database.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    with db_session as session:
        result =  session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username},
        )
        return result.scalar() is not None


async def validate_expense_id(expense_id: str):
    """
    Validates if the expense ID exists in the database.

    Args:
        expense_id (str): The expense ID to check.

    Returns:
        bool: True if the expense ID exists, False otherwise.
    """
    with db_session as session:
        result =  session.execute(
            text("SELECT * FROM expenses WHERE id = :id"), {"id": expense_id}
        )
        return result.scalar() is not None


async def validate_income_id(income_id: str):
    """
    Validates if the income ID exists in the database.

    Args:
        income_id (str): The income ID to check.

    Returns:
        bool: True if the income ID exists, False otherwise.
    """
    with db_session as session:
        result =  session.execute(
            text("SELECT * FROM incomes WHERE id = :id"), {"id": income_id}
        )
        return result.scalar() is not None


async def validate_message_not_empty(message: str):
    """
    Validates if the message is not empty.

    Args:
        message (str): The message to check.

    Returns:
        bool: True if the message is not empty, False otherwise.
    """
    return bool(message.strip())
