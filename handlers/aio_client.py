"""
This module handles the API requests for the Telegram bot.
"""

import aiohttp
import logging
import asyncio
from typing import Dict, Any, Optional
from config import API_BASE_URL
from keyboards import (
    get_start_keyboard,
    get_back_to_start_keyboard,
)

logging.basicConfig(level=logging.INFO)


async def api_request_with_retry(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    retries: int = 3,
) -> Dict[str, Any]:
    """
    Makes an HTTP request to the API with retry mechanism.

    Args:
        method (str): HTTP method to use (e.g., "POST", "GET").
        endpoint (str): API endpoint to interact with.
        params (dict, optional): Query parameters for the API request.
        json (dict, optional): Data to send in the request body.
        headers (dict, optional): Additional headers for the request.
        retries (int): Number of retry attempts for transient errors.

    Returns:
        dict: JSON response from the API.

    Raises:
        Exception: Raises an exception for HTTP errors or connection issues.
    """
    url = f"{API_BASE_URL}/{endpoint}"
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, params=params, json=json, headers=headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"Network error on attempt {attempt + 1}: {str(e)}")
            if attempt == retries - 1:
                raise Exception(f"Network error after {retries} attempts: {str(e)}")
            await asyncio.sleep(2**attempt)


async def handle_api_request(
    method: str,
    params: Dict[str, Any],
    endpoint: str,
    payload: Optional[Dict[str, Any]],
    success_message: str,
    error_message: str,
    msg: Any,
) -> None:
    """
    Handles API requests and sends messages based on the response.

    Args:
        method (str): HTTP method to use (e.g., "POST", "GET").
        params (dict): Parameters for the API request.
        endpoint (str): API endpoint to interact with.
        payload (dict, optional): Data to send in the request body.
        success_message (str): Message to send on a successful response.
        error_message (str): Message to send on an error response.
        msg (Any): Message object to respond to the user.
    """
    try:
        response = await api_request_with_retry(
            method, endpoint, params=params, json=payload
        )
        if response.get("status") == "success":
            await msg.answer(success_message, reply_markup=get_start_keyboard())
        else:
            logging.warning(f"Unexpected response: {response}")
            raise Exception(error_message)
    except Exception as e:
        await msg.answer(
            f"Error: {str(e)}. Please try again later.",
            reply_markup=get_back_to_start_keyboard(),
        )


async def generate_csv_report(chat_id: str, msg: Any) -> None:
    """
    Requests a CSV report from the API and sends the file name to the user.

    Args:
        chat_id (str): User's chat ID to include in the request.
        msg (Any): Message object to respond to the user.
    """
    params = {"chat_id": chat_id}
    await handle_api_request(
        "GET",
        params,
        "generate_csv_report",
        None,
        "CSV report generated successfully.",
        "Failed to generate CSV report.",
        msg,
    )


async def generate_excel_report(chat_id: str, msg: Any) -> None:
    """
    Requests an Excel report from the API and sends the file name to the user.

    Args:
        chat_id (str): User's chat ID to include in the request.
        msg (Any): Message object to respond to the user.
    """
    params = {"chat_id": chat_id}
    await handle_api_request(
        "GET",
        params,
        "generate_excel_report",
        None,
        "Excel report generated successfully.",
        "Failed to generate Excel report.",
        msg,
    )
