"""
This module provides utility functions for generating reports,
including report generation in CSV and XLSX formats.
"""

import csv
import openpyxl

from db import User, db_session


def get_all_users():
    """
    Retrieves all users from the database.

    Returns:
        list: A list of User objects representing all users in the database.
    """
    return db_session.query(User).all()


def generate_csv_report():
    """
    Generates a CSV report of all users in the database and saves it to a file.

    The CSV file includes the user's ID, username, email, and a placeholder for balance.

    Returns:
        str: The path to the generated CSV report file.
    """
    file_path = "report.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Username", "Email", "Balance"])
        for user in get_all_users():
            writer.writerow([user.id, user.username, user.email, "Balance Placeholder"])
    return file_path


def generate_xlsx_report():
    """
    Generates an XLSX report of all users in the database and saves it to a file.

    The XLSX file includes the user's ID, username, email, and a placeholder for balance.

    Returns:
        str: The path to the generated XLSX report file.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "User Report"

    headers = ["ID", "Username", "Email", "Balance"]
    sheet.append(headers)

    for user in get_all_users():
        sheet.append([user.id, user.username, user.email, "Balance Placeholder"])

    file_path = "report.xlsx"
    workbook.save(file_path)
    return file_path
