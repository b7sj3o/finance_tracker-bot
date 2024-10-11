"""
This module handles the routes  the Telegram bot.
"""

import os
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards import (
    get_start_keyboard,
    get_report_keyboard,
    get_back_to_start_keyboard,
    get_expense_period_keyboard,
    get_income_period_keyboard,
)
from config import (
    dp,
    Expense,
    Income,
    API_ENDPOINT_INCOME,
    API_ENDPOINT_EXPENSE,
    MAX_AMOUNT,
    router,
)
from .validators import (
    validate_amount_description,
    validate_user_exists,
    validate_expense_id,
    validate_income_id,
    validate_message_not_empty,
)
from .aio_client import handle_api_request, generate_csv_report, generate_excel_report


@dp.message(F.text == "/start")
async def start(msg: Message, state: FSMContext):
    """
    Handles the /start command.
    """
    await msg.delete()
    user_exists = await validate_user_exists(msg.from_user.username)

    welcome_message = (
        f"Hello {msg.from_user.username}, you are logged in."
        if user_exists
        else "Welcome! Please choose an action:"
    )
    await msg.answer(
        welcome_message, reply_markup=get_start_keyboard() if not user_exists else None
    )


@dp.callback_query(F.data == "start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    """
    Navigates back to the start menu.
    """
    await callback.message.edit_text(
        "Welcome! Please choose an action:", reply_markup=get_start_keyboard()
    )


@dp.callback_query(F.data == "report")
async def report(callback: CallbackQuery, state: FSMContext):
    """
    Handles the report request and shows options for generating reports.
    """
    await callback.message.edit_text(
        "Please choose how you'd like to receive your report or specify the format.",
        reply_markup=get_report_keyboard(),
    )


async def send_report(
    callback: CallbackQuery, file_path: str, success_message: str, failure_message: str
):
    """
    Sends the report file to the user and handles file cleanup.
    """
    try:
        with open(file_path, "rb") as file:
            await callback.message.answer_document(file)
        os.remove(file_path)
        await callback.message.answer(
            success_message, reply_markup=get_start_keyboard()
        )
    except Exception as e:
        await callback.message.answer(
            f"{failure_message}\nError: {str(e)}", reply_markup=get_start_keyboard()
        )


@dp.callback_query(F.data == "get_report")
async def get_report(callback: CallbackQuery, state: FSMContext):
    """
    Generates and sends the CSV report to the user.
    """
    file_path = generate_csv_report()
    await send_report(
        callback,
        file_path,
        "Here is your report.",
        "Failed to generate report. Please try again later.",
    )


@dp.callback_query(F.data == "generate_excel_report")
async def generate_excel(callback: CallbackQuery, state: FSMContext):
    """
    Generates and sends the Excel report to the user.
    """
    file_path = generate_excel_report()
    await send_report(
        callback,
        file_path,
        "Here is your Excel report.",
        "Failed to generate Excel report. Please try again later.",
    )


@dp.callback_query(F.data == "view_expenses")
async def view_expenses(callback: CallbackQuery, state: FSMContext):
    """
    Displays options for viewing expenses based on the selected period.
    """
    await callback.message.edit_text(
        "Choose the period to view expenses:",
        reply_markup=get_expense_period_keyboard(),
    )


@dp.callback_query(F.data == "add_expense")
async def add_expense(callback: CallbackQuery, state: FSMContext):
    """
    Prompts the user to enter expense details.
    """
    await callback.message.edit_text(
        "Please enter the expense details in the following format:\n\nAmount Description",
        reply_markup=get_back_to_start_keyboard(),
    )
    await state.set_state(Expense.waiting_for_expense_details)


@dp.message(Expense.waiting_for_expense_details)
async def process_expense_details(msg: Message, state: FSMContext):
    """
    Processes the expense details provided by the user.
    """
    if not await validate_message_not_empty(msg.text):
        return await msg.answer(
            "Input cannot be empty. Please provide the details.",
            reply_markup=get_back_to_start_keyboard(),
        )

    amount, description = await validate_amount_description(msg.text)
    if amount is None:
        return await msg.answer(description, reply_markup=get_back_to_start_keyboard())

    if amount > MAX_AMOUNT:
        return await msg.answer(
            f"Amount cannot exceed {MAX_AMOUNT}.",
            reply_markup=get_back_to_start_keyboard(),
        )

    user_exists = await validate_user_exists(msg.from_user.username)
    if user_exists:
        payload = {"amount": amount, "description": description}
        await handle_api_request(
            "POST",
            API_ENDPOINT_EXPENSE,
            payload,
            "Expense added successfully.",
            "Failed to add expense. Please try again later.",
            msg,
            params={"chat_id": msg.from_user.id},  # Add chat_id
        )
    else:
        await msg.answer(
            "User not found. Please register.", reply_markup=get_start_keyboard()
        )

    await state.clear()


@dp.callback_query(F.data == "update_expense")
async def update_expense(callback: CallbackQuery, state: FSMContext):
    """
    Prompts the user to enter the ID of the expense they want to update.
    """
    await callback.message.edit_text(
        "Please enter the ID of the expense you want to update, followed by the new details in the format:\n\nID Amount Description",
        reply_markup=get_back_to_start_keyboard(),
    )
    await state.set_state(Expense.waiting_for_update_details)


@dp.message(Expense.waiting_for_update_details)
async def process_expense_update_details(msg: Message, state: FSMContext):
    """
    Processes the update details for an expense provided by the user.
    """
    if not await validate_message_not_empty(msg.text):
        return await msg.answer(
            "Input cannot be empty. Please provide the details.",
            reply_markup=get_back_to_start_keyboard(),
        )

    update_details = msg.text.split(" ", 2)
    if len(update_details) != 3:
        return await msg.answer(
            "Invalid format. Please use 'ID Amount Description'.",
            reply_markup=get_back_to_start_keyboard(),
        )

    expense_id, *details = update_details
    amount, description = await validate_amount_description(" ".join(details))
    if amount is None:
        return await msg.answer(description, reply_markup=get_back_to_start_keyboard())

    if amount > MAX_AMOUNT:
        return await msg.answer(
            f"Amount cannot exceed {MAX_AMOUNT}.",
            reply_markup=get_back_to_start_keyboard(),
        )

    is_valid_id = await validate_expense_id(expense_id)
    if not is_valid_id:
        return await msg.answer(
            "Expense ID not found. Please check and try again.",
            reply_markup=get_back_to_start_keyboard(),
        )

    user_exists = await validate_user_exists(msg.from_user.username)
    if user_exists:
        payload = {"amount": amount, "description": description}
        await handle_api_request(
            "PUT",
            f"{API_ENDPOINT_EXPENSE}{expense_id}/",
            payload,
            "Expense updated successfully.",
            "Failed to update expense. Please try again later.",
            msg,
            params={"chat_id": msg.from_user.id},  # Add chat_id
        )
    else:
        await msg.answer(
            "User not found. Please register.", reply_markup=get_start_keyboard()
        )

    await state.clear()


@dp.callback_query(F.data == "delete_expense")
async def delete_expense(callback: CallbackQuery, state: FSMContext):
    """
    Prompts the user to enter the ID of the expense they want to delete.
    """
    await callback.message.edit_text(
        "Please enter the ID of the expense you want to delete.",
        reply_markup=get_back_to_start_keyboard(),
    )
    await state.set_state(Expense.waiting_for_delete_id)


@dp.message(Expense.waiting_for_delete_id)
async def process_delete_expense(msg: Message, state: FSMContext):
    """
    Processes the delete request for an expense.
    """
    if not await validate_message_not_empty(msg.text):
        return await msg.answer(
            "Input cannot be empty. Please provide the ID.",
            reply_markup=get_back_to_start_keyboard(),
        )

    expense_id = msg.text.strip()
    is_valid_id = await validate_expense_id(expense_id)
    if not is_valid_id:
        return await msg.answer(
            "Expense ID not found. Please check and try again.",
            reply_markup=get_back_to_start_keyboard(),
        )

    user_exists = await validate_user_exists(msg.from_user.username)
    if user_exists:
        await handle_api_request(
            "DELETE",
            f"{API_ENDPOINT_EXPENSE}{expense_id}/",
            None,
            "Expense deleted successfully.",
            "Failed to delete expense. Please try again later.",
            msg,
            params={"chat_id": msg.from_user.id},  # Add chat_id
        )
    else:
        await msg.answer(
            "User not found. Please register.", reply_markup=get_start_keyboard()
        )

    await state.clear()


@dp.callback_query(F.data == "view_income")
async def view_income(callback: CallbackQuery, state: FSMContext):
    """
    Displays options for viewing income based on the selected period.
    """
    await callback.message.edit_text(
        "Choose the period to view income:", reply_markup=get_income_period_keyboard()
    )


@dp.callback_query(F.data == "add_income")
async def add_income(callback: CallbackQuery, state: FSMContext):
    """
    Prompts the user to enter income details.
    """
    await callback.message.edit_text(
        "Please enter the income details in the following format:\n\nAmount Description",
        reply_markup=get_back_to_start_keyboard(),
    )
    await state.set_state(Income.waiting_for_income_details)


@dp.message(Income.waiting_for_income_details)
async def process_income_details(msg: Message, state: FSMContext):
    """
    Processes the income details provided by the user.
    """
    if not await validate_message_not_empty(msg.text):
        return await msg.answer(
            "Input cannot be empty. Please provide the details.",
            reply_markup=get_back_to_start_keyboard(),
        )

    amount, description = await validate_amount_description(msg.text)
    if amount is None:
        return await msg.answer(description, reply_markup=get_back_to_start_keyboard())

    if amount > MAX_AMOUNT:
        return await msg.answer(
            f"Amount cannot exceed {MAX_AMOUNT}.",
            reply_markup=get_back_to_start_keyboard(),
        )

    user_exists = await validate_user_exists(msg.from_user.username)
    if user_exists:
        payload = {"amount": amount, "description": description}
        await handle_api_request(
            "POST",
            API_ENDPOINT_INCOME,
            payload,
            "Income added successfully.",
            "Failed to add income. Please try again later.",
            msg,
            params={"chat_id": msg.from_user.id},  # Add chat_id
        )
    else:
        await msg.answer(
            "User not found. Please register.", reply_markup=get_start_keyboard()
        )

    await state.clear()


@dp.callback_query(F.data == "update_income")
async def update_income(callback: CallbackQuery, state: FSMContext):
    """
    Prompts the user to enter the ID of the income they want to update.
    """
    await callback.message.edit_text(
        "Please enter the ID of the income you want to update, followed by the new details in the format:\n\nID Amount Description",
        reply_markup=get_back_to_start_keyboard(),
    )
    await state.set_state(Income.waiting_for_update_details)


@dp.message(Income.waiting_for_update_details)
async def process_income_update_details(msg: Message, state: FSMContext):
    """
    Processes the update details for income provided by the user.
    """
    if not await validate_message_not_empty(msg.text):
        return await msg.answer(
            "Input cannot be empty. Please provide the details.",
            reply_markup=get_back_to_start_keyboard(),
        )

    update_details = msg.text.split(" ", 2)
    if len(update_details) != 3:
        return await msg.answer(
            "Invalid format. Please use 'ID Amount Description'.",
            reply_markup=get_back_to_start_keyboard(),
        )

    income_id, *details = update_details
    amount, description = await validate_amount_description(" ".join(details))
    if amount is None:
        return await msg.answer(description, reply_markup=get_back_to_start_keyboard())

    if amount > MAX_AMOUNT:
        return await msg.answer(
            f"Amount cannot exceed {MAX_AMOUNT}.",
            reply_markup=get_back_to_start_keyboard(),
        )

    is_valid_id = await validate_income_id(income_id)
    if not is_valid_id:
        return await msg.answer(
            "Income ID not found. Please check and try again.",
            reply_markup=get_back_to_start_keyboard(),
        )

    user_exists = await validate_user_exists(msg.from_user.username)
    if user_exists:
        payload = {"amount": amount, "description": description}
        await handle_api_request(
            "PUT",
            f"{API_ENDPOINT_INCOME}{income_id}/",
            payload,
            "Income updated successfully.",
            "Failed to update income. Please try again later.",
            msg,
            params={"chat_id": msg.from_user.id},  # Add chat_id
        )
    else:
        await msg.answer(
            "User not found. Please register.", reply_markup=get_start_keyboard()
        )

    await state.clear()


@dp.callback_query(F.data == "delete_income")
async def delete_income(callback: CallbackQuery, state: FSMContext):
    """
    Prompts the user to enter the ID of the income they want to delete.
    """
    await callback.message.edit_text(
        "Please enter the ID of the income you want to delete.",
        reply_markup=get_back_to_start_keyboard(),
    )
    await state.set_state(Income.waiting_for_delete_id)


@dp.message(Income.waiting_for_delete_id)
async def process_delete_income(msg: Message, state: FSMContext):
    """
    Processes the delete request for income.
    """
    if not await validate_message_not_empty(msg.text):
        return await msg.answer(
            "Input cannot be empty. Please provide the ID.",
            reply_markup=get_back_to_start_keyboard(),
        )

    income_id = msg.text.strip()
    is_valid_id = await validate_income_id(income_id)
    if not is_valid_id:
        return await msg.answer(
            "Income ID not found. Please check and try again.",
            reply_markup=get_back_to_start_keyboard(),
        )

    user_exists = await validate_user_exists(msg.from_user.username)
    if user_exists:
        await handle_api_request(
            "DELETE",
            f"{API_ENDPOINT_INCOME}{income_id}/",
            None,
            "Income deleted successfully.",
            "Failed to delete income. Please try again later.",
            msg,
            params={"chat_id": msg.from_user.id},  # Add chat_id
        )
    else:
        await msg.answer(
            "User not found. Please register.", reply_markup=get_start_keyboard()
        )

    await state.clear()
