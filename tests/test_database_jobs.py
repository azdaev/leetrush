from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import make_task


MSK = timezone(timedelta(hours=3))


async def test_schedule_job_inserts_pending(test_db):
    task_id = await make_task(test_db)
    fire_at = datetime.now(MSK) + timedelta(hours=1)

    await test_db.schedule_job(task_id, "reminder_1h", fire_at)

    now = datetime.now(MSK) + timedelta(hours=2)
    jobs = await test_db.get_due_jobs(now)
    assert len(jobs) == 1
    assert jobs[0]["task_id"] == task_id
    assert jobs[0]["kind"] == "reminder_1h"
    assert jobs[0]["status"] == "pending"


async def test_schedule_job_unique_per_task_kind(test_db):
    """UNIQUE(task_id, kind) — повторный INSERT игнорируется."""
    task_id = await make_task(test_db)
    fire_at = datetime.now(MSK) + timedelta(hours=1)

    await test_db.schedule_job(task_id, "reminder_1h", fire_at)
    await test_db.schedule_job(task_id, "reminder_1h", fire_at + timedelta(minutes=30))

    now = datetime.now(MSK) + timedelta(hours=3)
    jobs = await test_db.get_due_jobs(now)
    assert len(jobs) == 1, "дубль должен быть проигнорирован"


async def test_different_kinds_for_same_task_coexist(test_db):
    task_id = await make_task(test_db)
    base = datetime.now(MSK) - timedelta(minutes=1)

    await test_db.schedule_job(task_id, "reminder_24h", base)
    await test_db.schedule_job(task_id, "reminder_1h", base)
    await test_db.schedule_job(task_id, "close_deadline", base)

    jobs = await test_db.get_due_jobs(datetime.now(MSK))
    kinds = {j["kind"] for j in jobs}
    assert kinds == {"reminder_24h", "reminder_1h", "close_deadline"}


async def test_get_due_jobs_filters_by_fire_at(test_db):
    task_id = await make_task(test_db)
    past = datetime.now(MSK) - timedelta(minutes=1)
    future = datetime.now(MSK) + timedelta(hours=10)

    await test_db.schedule_job(task_id, "reminder_24h", past)
    await test_db.schedule_job(task_id, "reminder_1h", future)

    due = await test_db.get_due_jobs(datetime.now(MSK))
    assert len(due) == 1
    assert due[0]["kind"] == "reminder_24h"


async def test_get_due_jobs_filters_by_status(test_db):
    task_id = await make_task(test_db)
    past = datetime.now(MSK) - timedelta(minutes=1)

    await test_db.schedule_job(task_id, "reminder_1h", past)

    due = await test_db.get_due_jobs(datetime.now(MSK))
    assert len(due) == 1
    await test_db.mark_job_done(due[0]["id"])

    due_after = await test_db.get_due_jobs(datetime.now(MSK))
    assert len(due_after) == 0


async def test_mark_job_done_sets_status_and_fired_at(test_db):
    task_id = await make_task(test_db)
    await test_db.schedule_job(task_id, "reminder_1h", datetime.now(MSK) - timedelta(minutes=1))

    due = await test_db.get_due_jobs(datetime.now(MSK))
    job_id = due[0]["id"]
    await test_db.mark_job_done(job_id)

    import aiosqlite
    async with aiosqlite.connect(test_db.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM scheduled_jobs WHERE id = ?", (job_id,))
        row = await cursor.fetchone()
    assert row["status"] == "done"
    assert row["fired_at"] is not None


async def test_mark_job_failed_sets_status(test_db):
    task_id = await make_task(test_db)
    await test_db.schedule_job(task_id, "reminder_1h", datetime.now(MSK) - timedelta(minutes=1))

    due = await test_db.get_due_jobs(datetime.now(MSK))
    job_id = due[0]["id"]
    await test_db.mark_job_failed(job_id)

    import aiosqlite
    async with aiosqlite.connect(test_db.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM scheduled_jobs WHERE id = ?", (job_id,))
        row = await cursor.fetchone()
    assert row["status"] == "failed"
    assert row["fired_at"] is not None


async def test_get_task_by_id(test_db):
    task_id = await make_task(test_db, number=42, title="Foo")

    task = await test_db.get_task_by_id(task_id)
    assert task["number"] == 42
    assert task["title"] == "Foo"

    missing = await test_db.get_task_by_id(9999)
    assert missing is None
