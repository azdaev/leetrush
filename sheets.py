import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_CREDENTIALS_FILE, SHEETS_ID

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Цвета
GREEN = {"red": 0.714, "green": 0.843, "blue": 0.659}   # #B6D7A8
RED   = {"red": 0.918, "green": 0.6,   "blue": 0.6}     # #EA9999
WHITE = {"red": 1.0,   "green": 1.0,   "blue": 1.0}

# Строки в таблице
HEADER_ROW = 1   # №, Задача, Дедлайн, User1, User2...
DATA_ROW_OFFSET = 2  # задачи начинаются со строки 2


SHEET_GID = 1112096595


def _get_sheet():
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEETS_ID)
    return spreadsheet.get_worksheet_by_id(SHEET_GID)


def _col_letter(col_index: int) -> str:
    """0-based index → буква колонки (0=A, 1=B, ...)"""
    result = ""
    col_index += 1
    while col_index:
        col_index, remainder = divmod(col_index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def get_header_row() -> list[str]:
    """Возвращает все заголовки первой строки."""
    sheet = _get_sheet()
    return sheet.row_values(HEADER_ROW)


def find_col_by_name(name: str) -> int | None:
    """Ищет колонку по имени в заголовке. Возвращает 0-based index или None."""
    headers = get_header_row()
    name_lower = name.lower().strip()
    for i, h in enumerate(headers):
        if h.lower().strip() == name_lower:
            return i
    return None


def get_next_col_index() -> int:
    """Возвращает следующий свободный 0-based индекс колонки."""
    headers = get_header_row()
    return len(headers)


def setup_sheet():
    """Инициализирует заголовки таблицы если пусто."""
    sheet = _get_sheet()
    headers = sheet.row_values(HEADER_ROW)
    if not headers:
        sheet.update(f"A{HEADER_ROW}:C{HEADER_ROW}", [["№", "Задача", "Дедлайн"]])
        _format_header(sheet, "A1:C1")


def _format_header(sheet, range_str: str):
    sheet.spreadsheet.batch_update({
        "requests": [{
            "repeatCell": {
                "range": _parse_range(sheet, range_str),
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.267, "green": 0.267, "blue": 0.267},
                        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat"
            }
        }]
    })


def _parse_range(sheet, range_str: str) -> dict:
    sheet_id = sheet.id
    # простой парсер A1:C1
    import re
    match = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", range_str)
    if not match:
        return {}
    def col_idx(letters):
        result = 0
        for ch in letters:
            result = result * 26 + (ord(ch) - ord('A') + 1)
        return result - 1
    sc, sr, ec, er = match.groups()
    return {
        "sheetId": sheet_id,
        "startRowIndex": int(sr) - 1,
        "endRowIndex": int(er),
        "startColumnIndex": col_idx(sc),
        "endColumnIndex": col_idx(ec) + 1,
    }


def add_participant_column(first_name: str, sheet_col: int):
    """Добавляет колонку участника в заголовок."""
    sheet = _get_sheet()
    col_letter = _col_letter(sheet_col)
    sheet.update(f"{col_letter}{HEADER_ROW}", [[first_name]])
    sheet.spreadsheet.batch_update({
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": HEADER_ROW - 1,
                    "endRowIndex": HEADER_ROW,
                    "startColumnIndex": sheet_col,
                    "endColumnIndex": sheet_col + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.267, "green": 0.267, "blue": 0.267},
                        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat"
            }
        }]
    })


def add_task_row(task_number: int, title: str, deadline_str: str):
    """Добавляет строку задачи."""
    sheet = _get_sheet()
    row = DATA_ROW_OFFSET + (task_number - 12)  # задачи с #12
    sheet.update(f"A{row}:C{row}", [[f"#{task_number}", title, deadline_str]])


def mark_cell(task_number: int, sheet_col: int, done: bool):
    """Красит ячейку зелёным (done) или белым (undone)."""
    sheet = _get_sheet()
    row = DATA_ROW_OFFSET + (task_number - 12)
    color = GREEN if done else WHITE
    sheet.spreadsheet.batch_update({
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": sheet_col,
                    "endColumnIndex": sheet_col + 1,
                },
                "cell": {"userEnteredFormat": {"backgroundColor": color}},
                "fields": "userEnteredFormat.backgroundColor"
            }
        }]
    })


def mark_strike(task_number: int, sheet_col: int):
    """Красная ячейка + текст 'страйк'."""
    sheet = _get_sheet()
    row = DATA_ROW_OFFSET + (task_number - 12)
    col_letter = _col_letter(sheet_col)
    sheet.update(f"{col_letter}{row}", [["страйк"]])
    sheet.spreadsheet.batch_update({
        "requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": sheet_col,
                    "endColumnIndex": sheet_col + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": RED,
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.horizontalAlignment"
            }
        }]
    })
