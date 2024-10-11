from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Creates the start keyboard with options for user actions.

    Returns:
        InlineKeyboardMarkup: An inline keyboard markup with options for report generation, viewing and managing expenses, and other actions.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="About", callback_data="about")],
            [InlineKeyboardButton(text="Report", callback_data="report")],
            [InlineKeyboardButton(text="View Expenses", callback_data="view_expenses")],
            [InlineKeyboardButton(text="Add Expense", callback_data="add_expense")],
            [InlineKeyboardButton(text="Edit Expense", callback_data="edit_expense")],
            [
                InlineKeyboardButton(
                    text="Delete Expense", callback_data="delete_expense"
                )
            ],
            [InlineKeyboardButton(text="View History", callback_data="view_history")],
        ]
    )


def get_report_keyboard() -> InlineKeyboardMarkup:
    """
    Creates the report keyboard with options for generating a report or returning to the start menu.

    Returns:
        InlineKeyboardMarkup: An inline keyboard markup with options for generating a report or returning to the start menu.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Generate Report", callback_data="get_report")],
            [InlineKeyboardButton(text="Back to Start", callback_data="start")],
        ]
    )


def get_back_to_start_keyboard() -> InlineKeyboardMarkup:
    """
    Creates a keyboard with a single button to return to the start menu.

    Returns:
        InlineKeyboardMarkup: An inline keyboard markup with a button to return to the start menu.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Back to Start", callback_data="start")],
        ]
    )


def get_expense_period_keyboard() -> InlineKeyboardMarkup:
    """
    Creates a keyboard for selecting the expense period (daily, monthly, yearly) or returning to the start menu.

    Returns:
        InlineKeyboardMarkup: An inline keyboard markup with buttons for selecting the expense period or returning to the start menu.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Daily", callback_data="view_daily_expenses")],
            [
                InlineKeyboardButton(
                    text="Monthly", callback_data="view_monthly_expenses"
                )
            ],
            [InlineKeyboardButton(text="Yearly", callback_data="view_yearly_expenses")],
            [InlineKeyboardButton(text="Back to Start", callback_data="start")],
        ]
    )


def get_income_period_keyboard() -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for selecting the period to view incomes.

    Returns:
        InlineKeyboardMarkup: An inline keyboard markup with buttons for different income periods.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)

    buttons = [
        InlineKeyboardButton(text="Today", callback_data="income_today"),
        InlineKeyboardButton(text="This Week", callback_data="income_week"),
        InlineKeyboardButton(text="This Month", callback_data="income_month"),
        InlineKeyboardButton(text="This Year", callback_data="income_year"),
        InlineKeyboardButton(text="All Time", callback_data="income_all_time"),
    ]

    keyboard.add(*buttons)

    return keyboard
