import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import database as db


@pytest_asyncio.fixture
async def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", str(db_path))
    await db.init_db()
    return db


@pytest.fixture
def mock_bot():
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    return bot


async def make_task(database, number=12, title="Reverse String", status="active", deadline=None):
    """Создаёт задачу в БД и возвращает её id."""
    import aiosqlite
    async with aiosqlite.connect(database.DB_PATH) as conn:
        cursor = await conn.execute(
            """INSERT INTO tasks (number, title, url, topic, difficulty, status, deadline)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (number, title, "https://leetcode.com/problems/x", "Two Pointers", "easy", status,
             deadline.isoformat() if deadline else None),
        )
        await conn.commit()
        return cursor.lastrowid


async def make_participant(database, user_id, first_name="User", username=None, sheet_col=4):
    import aiosqlite
    async with aiosqlite.connect(database.DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO participants (user_id, username, first_name, sheet_col) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, sheet_col),
        )
        await conn.commit()
