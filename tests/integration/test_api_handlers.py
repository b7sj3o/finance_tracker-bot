import pytest

from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from unittest.mock import AsyncMock

from ...config import Expense
from ...handlers import add_expense, process_expense_details


# TODO: хуйня то всьо, якщо запускати як в файлі scripts/run_tests.sh, то bot/__init__.py просто не бачить пакетів


@pytest.fixture
def message():
    return Message(
        message_id=1, date=None, chat=None, from_user=None, text="/add_expense"
    )


@pytest.fixture
def callback_query():
    return CallbackQuery(
        id="1", from_user=None, message=AsyncMock(), data="add_expense"
    )


@pytest.mark.asyncio
async def test_add_expense_handler(callback_query, mock_state):
    """
    First handler that is waiting for details after typing /add_expense
    """
    await add_expense(callback_query, mock_state)

    callback_query.message.edit_text.assert_called_with(
        "Please enter the expense details in the following format:\n\nAmount Description",
        reply_markup=mock_state.get_back_to_start_keyboard.return_value,
    )

    mock_state.set_state.assert_called_with(Expense.waiting_for_expense_details)


@pytest.mark.asyncio
async def test_process_expense_details_valid(message, mock_state):
    """
    Тестуємо другий хендлер, який обробляє введені деталі витрати.
    """
    message.text = "100 Lunch"

    mock_validate_message_not_empty = AsyncMock(return_value=True)
    mock_validate_amount_description = AsyncMock(return_value=(100, "Lunch"))
    mock_validate_user_exists = AsyncMock(return_value=True)
    mock_handle_api_request = AsyncMock()

    mock_state.get_state.return_value = Expense.waiting_for_expense_details

    with pytest.monkeypatch.context() as m:
        m.setattr(
            "..handlers.validate_message_not_empty", mock_validate_message_not_empty
        )
        m.setattr(
            "..handlers.validate_amount_description", mock_validate_amount_description
        )
        m.setattr("..handlers.validate_user_exists", mock_validate_user_exists)
        m.setattr("..handlers.handle_api_request", mock_handle_api_request)

        await process_expense_details(message, mock_state)

        mock_handle_api_request.assert_called_with(
            "POST",
            "expense",
            {"amount": 100, "description": "Lunch"},
            "Expense added successfully.",
            "Failed to add expense. Please try again later.",
            message,
            params={"chat_id": message.from_user.id},
        )

        mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_process_expense_details_invalid(message, mock_state):
    """
    Тестуємо хендлер з некоректним введенням (наприклад, порожнє повідомлення).
    """
    message.text = ""

    mock_validate_message_not_empty = AsyncMock(return_value=False)

    with pytest.monkeypatch.context() as m:
        m.setattr(
            "..handlers.validate_message_not_empty", mock_validate_message_not_empty
        )

        await process_expense_details(message, mock_state)

        message.answer.assert_called_with(
            "Input cannot be empty. Please provide the details.",
            reply_markup=mock_state.get_back_to_start_keyboard.return_value,
        )
