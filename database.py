import aiosqlite
from datetime import datetime

DB_PATH = "data/leetrush.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS participants (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT NOT NULL,
                sheet_col   INTEGER,
                strikes     INTEGER DEFAULT 0,
                registered_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                number      INTEGER UNIQUE NOT NULL,
                title       TEXT NOT NULL,
                url         TEXT NOT NULL,
                topic       TEXT NOT NULL,
                difficulty  TEXT NOT NULL,
                deadline    TEXT,
                message_id  INTEGER,
                status      TEXT DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS completions (
                task_id     INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                done_at     TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (task_id, user_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (user_id) REFERENCES participants(user_id)
            );

            CREATE TABLE IF NOT EXISTS strike_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                task_id     INTEGER NOT NULL,
                created_at  TEXT DEFAULT (datetime('now')),
                UNIQUE(user_id, task_id),
                FOREIGN KEY (user_id) REFERENCES participants(user_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );

            CREATE TABLE IF NOT EXISTS scheduled_jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id     INTEGER NOT NULL,
                kind        TEXT NOT NULL,
                fire_at     TEXT NOT NULL,
                status      TEXT DEFAULT 'pending',
                fired_at    TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );
        """)
        # Migration for existing DBs without the unique constraint
        await db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_strike_log_unique ON strike_log (user_id, task_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_due ON scheduled_jobs (status, fire_at)"
        )
        await db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_scheduled_jobs_task_kind ON scheduled_jobs (task_id, kind)"
        )
        await db.commit()


# --- Participants ---

async def register_participant(user_id: int, username: str | None, first_name: str, sheet_col: int) -> bool:
    """Возвращает True если зарегистрирован впервые. sheet_col передаётся снаружи."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM participants WHERE user_id = ?", (user_id,)
        )
        exists = await cursor.fetchone()
        if exists:
            await db.execute(
                "UPDATE participants SET username = ?, first_name = ? WHERE user_id = ?",
                (username, first_name, user_id)
            )
            await db.commit()
            return False

        await db.execute(
            "INSERT INTO participants (user_id, username, first_name, sheet_col) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, sheet_col)
        )
        await db.commit()
        return True


async def get_participant(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM participants WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone()


async def get_all_participants():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM participants ORDER BY sheet_col"
        )
        return await cursor.fetchall()


# --- Tasks ---

async def load_tasks_pool(tasks: list[dict]):
    """Синхронизирует пул задач: удаляет pending и загружает из списка заново.
    Активные и закрытые задачи не трогает."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE status = 'pending'")
        await db.executemany(
            """INSERT OR IGNORE INTO tasks (number, title, url, topic, difficulty)
               VALUES (?, ?, ?, ?, ?)""",
            [(t["number"], t["title"], t["url"], t["topic"], t["difficulty"]) for t in tasks]
        )
        await db.commit()


async def get_next_pending_task():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM tasks WHERE status = 'pending' ORDER BY number LIMIT 1"
        )
        return await cursor.fetchone()


async def get_active_task():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM tasks WHERE status = 'active' LIMIT 1"
        )
        return await cursor.fetchone()


async def activate_task(task_id: int, deadline: datetime, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET status = 'active', deadline = ?, message_id = ? WHERE id = ?",
            (deadline.isoformat(), message_id, task_id)
        )
        await db.commit()


async def close_task(task_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET status = 'closed' WHERE id = ?", (task_id,)
        )
        await db.commit()


async def get_task_by_number(number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM tasks WHERE number = ?", (number,)
        )
        return await cursor.fetchone()


async def get_task_by_id(task_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        )
        return await cursor.fetchone()


async def get_all_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM tasks ORDER BY number")
        return await cursor.fetchall()


# --- Completions ---

async def mark_done(task_id: int, user_id: int) -> bool:
    """Возвращает True если отметка новая."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO completions (task_id, user_id) VALUES (?, ?)",
                (task_id, user_id)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def unmark_done(task_id: int, user_id: int) -> bool:
    """Возвращает True если отметка была."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM completions WHERE task_id = ? AND user_id = ?",
            (task_id, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_completions(task_id: int) -> list[int]:
    """Возвращает список user_id кто выполнил задачу."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM completions WHERE task_id = ?", (task_id,)
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def has_done(task_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM completions WHERE task_id = ? AND user_id = ?",
            (task_id, user_id)
        )
        return await cursor.fetchone() is not None


# --- Strikes ---

async def add_strike(user_id: int, task_id: int) -> int:
    """Добавляет страйк и возвращает новое общее количество. Идемпотентно."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT OR IGNORE INTO strike_log (user_id, task_id) VALUES (?, ?)",
            (user_id, task_id)
        )
        if cursor.rowcount > 0:
            await db.execute(
                "UPDATE participants SET strikes = strikes + 1 WHERE user_id = ?",
                (user_id,)
            )
        await db.commit()

        cursor = await db.execute(
            "SELECT strikes FROM participants WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0]


async def remove_strike(user_id: int) -> int:
    """Снимает один страйк (мин. 0). Удаляет последнюю запись из strike_log. Возвращает новый счёт."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT strikes FROM participants WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if not row or row[0] <= 0:
            return row[0] if row else 0

        await db.execute(
            "DELETE FROM strike_log WHERE id = (SELECT id FROM strike_log WHERE user_id = ? ORDER BY created_at DESC LIMIT 1)",
            (user_id,)
        )
        await db.execute(
            "UPDATE participants SET strikes = strikes - 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT strikes FROM participants WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0]


async def get_strikes_table():
    """Возвращает всех участников с их страйками."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM participants ORDER BY strikes DESC, first_name"
        )
        return await cursor.fetchall()


# --- Scheduled jobs ---

async def schedule_job(task_id: int, kind: str, fire_at: datetime):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO scheduled_jobs (task_id, kind, fire_at) VALUES (?, ?, ?)",
            (task_id, kind, fire_at.isoformat())
        )
        await db.commit()


async def get_due_jobs(now: datetime):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM scheduled_jobs WHERE status = 'pending' AND fire_at <= ? ORDER BY fire_at",
            (now.isoformat(),)
        )
        return await cursor.fetchall()


async def mark_job_done(job_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE scheduled_jobs SET status = 'done', fired_at = datetime('now') WHERE id = ?",
            (job_id,)
        )
        await db.commit()


async def mark_job_failed(job_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE scheduled_jobs SET status = 'failed', fired_at = datetime('now') WHERE id = ?",
            (job_id,)
        )
        await db.commit()
