import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message
from ...handlers import add_expense


@pytest.fixture
def message():
    return Message(
        message_id=1, date=None, chat=None, from_user=None, text="/add_expense"
    )


@pytest.mark.asyncio
@patch("bot.handlers.validate_user_exists", new_callable=AsyncMock)
async def test_add_expense_handler(mock_validate_user_exists, message):
    mock_validate_user_exists.return_value = False  # Юзер не існує

    response = await add_expense(message)
    
    assert "User not found. Please register." in response.text
