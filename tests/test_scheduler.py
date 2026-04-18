from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

import scheduler
from scheduler import (
    MOSCOW_TZ,
    schedule_task_jobs,
    run_jobs,
    _close_deadline,
    _send_reminder_24h,
    _send_reminder_1h,
)
from tests.conftest import make_task, make_participant


# ---------- schedule_task_jobs ----------

async def test_schedule_task_jobs_full_horizon(test_db):
    task_id = await make_task(test_db)
    deadline = datetime.now(MOSCOW_TZ) + timedelta(days=3)

    await schedule_task_jobs(task_id, deadline)

    due_soon = await test_db.get_due_jobs(datetime.now(MOSCOW_TZ) + timedelta(days=4))
    kinds = {j["kind"] for j in due_soon}
    assert kinds == {"reminder_24h", "reminder_1h", "close_deadline"}


async def test_schedule_task_jobs_skips_past_24h(test_db):
    task_id = await make_task(test_db)
    # дедлайн через 2 часа — reminder_24h в прошлом, пропускаем
    deadline = datetime.now(MOSCOW_TZ) + timedelta(hours=2)

    await schedule_task_jobs(task_id, deadline)

    jobs = await test_db.get_due_jobs(datetime.now(MOSCOW_TZ) + timedelta(days=1))
    kinds = {j["kind"] for j in jobs}
    assert kinds == {"reminder_1h", "close_deadline"}


async def test_schedule_task_jobs_only_close_for_short_deadline(test_db):
    task_id = await make_task(test_db)
    # дедлайн через 30 минут — и reminder_24h, и reminder_1h в прошлом
    deadline = datetime.now(MOSCOW_TZ) + timedelta(minutes=30)

    await schedule_task_jobs(task_id, deadline)

    jobs = await test_db.get_due_jobs(datetime.now(MOSCOW_TZ) + timedelta(hours=1))
    kinds = {j["kind"] for j in jobs}
    assert kinds == {"close_deadline"}


async def test_schedule_task_jobs_past_deadline_schedules_nothing(test_db):
    task_id = await make_task(test_db)
    deadline = datetime.now(MOSCOW_TZ) - timedelta(minutes=1)

    await schedule_task_jobs(task_id, deadline)

    jobs = await test_db.get_due_jobs(datetime.now(MOSCOW_TZ) + timedelta(days=1))
    assert jobs == []


# ---------- run_jobs ----------

async def test_run_jobs_dispatches_reminder_1h(test_db, mock_bot):
    task_id = await make_task(test_db, deadline=datetime.now(MOSCOW_TZ) + timedelta(hours=1))
    await test_db.schedule_job(task_id, "reminder_1h", datetime.now(MOSCOW_TZ) - timedelta(seconds=1))

    await run_jobs(mock_bot)

    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    text = args[1] if len(args) > 1 else kwargs.get("text", "")
    assert "Через час" in text
    assert "#12" in text


async def test_run_jobs_dispatches_reminder_24h(test_db, mock_bot):
    task_id = await make_task(test_db)
    await test_db.schedule_job(task_id, "reminder_24h", datetime.now(MOSCOW_TZ) - timedelta(seconds=1))

    await run_jobs(mock_bot)

    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    text = args[1] if len(args) > 1 else kwargs.get("text", "")
    assert "остался 1 день" in text


async def test_run_jobs_marks_done_after_success(test_db, mock_bot):
    task_id = await make_task(test_db)
    await test_db.schedule_job(task_id, "reminder_1h", datetime.now(MOSCOW_TZ) - timedelta(seconds=1))

    await run_jobs(mock_bot)

    # задача с такими параметрами больше не due
    remaining = await test_db.get_due_jobs(datetime.now(MOSCOW_TZ) + timedelta(minutes=1))
    assert remaining == []


async def test_run_jobs_skips_closed_tasks(test_db, mock_bot):
    task_id = await make_task(test_db, status="closed")
    await test_db.schedule_job(task_id, "reminder_1h", datetime.now(MOSCOW_TZ) - timedelta(seconds=1))

    await run_jobs(mock_bot)

    mock_bot.send_message.assert_not_called()
    # джоба помечена done, не failed
    due = await test_db.get_due_jobs(datetime.now(MOSCOW_TZ))
    assert due == []


async def test_run_jobs_marks_failed_on_handler_exception(test_db, mock_bot):
    task_id = await make_task(test_db)
    await test_db.schedule_job(task_id, "reminder_1h", datetime.now(MOSCOW_TZ) - timedelta(seconds=1))

    mock_bot.send_message.side_effect = RuntimeError("telegram down")
    await run_jobs(mock_bot)

    import aiosqlite
    async with aiosqlite.connect(test_db.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT status FROM scheduled_jobs")
        row = await cursor.fetchone()
    assert row["status"] == "failed"


async def test_run_jobs_ignores_not_due(test_db, mock_bot):
    task_id = await make_task(test_db)
    await test_db.schedule_job(task_id, "reminder_1h", datetime.now(MOSCOW_TZ) + timedelta(hours=1))

    await run_jobs(mock_bot)

    mock_bot.send_message.assert_not_called()


async def test_run_jobs_unknown_kind_marks_failed(test_db, mock_bot):
    task_id = await make_task(test_db)
    await test_db.schedule_job(task_id, "weird_kind", datetime.now(MOSCOW_TZ) - timedelta(seconds=1))

    await run_jobs(mock_bot)

    mock_bot.send_message.assert_not_called()
    import aiosqlite
    async with aiosqlite.connect(test_db.DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT status FROM scheduled_jobs")
        row = await cursor.fetchone()
    assert row["status"] == "failed"


# ---------- _close_deadline ----------

async def test_close_deadline_applies_strikes_only_to_non_solvers(test_db, mock_bot, monkeypatch):
    monkeypatch.setattr(scheduler.sheets, "mark_strike", lambda *a, **kw: None)

    task_id = await make_task(test_db)
    await make_participant(test_db, user_id=1, first_name="Solver", sheet_col=4)
    await make_participant(test_db, user_id=2, first_name="Loafer", sheet_col=5)
    await test_db.mark_done(task_id, 1)

    task = await test_db.get_task_by_id(task_id)
    await _close_deadline(mock_bot, task)

    # solver без страйков, loafer — 1 страйк
    solver = await test_db.get_participant(1)
    loafer = await test_db.get_participant(2)
    assert solver["strikes"] == 0
    assert loafer["strikes"] == 1


async def test_close_deadline_closes_task(test_db, mock_bot, monkeypatch):
    monkeypatch.setattr(scheduler.sheets, "mark_strike", lambda *a, **kw: None)

    task_id = await make_task(test_db)
    task = await test_db.get_task_by_id(task_id)
    await _close_deadline(mock_bot, task)

    closed = await test_db.get_task_by_id(task_id)
    assert closed["status"] == "closed"


async def test_close_deadline_is_idempotent_on_strikes(test_db, mock_bot, monkeypatch):
    monkeypatch.setattr(scheduler.sheets, "mark_strike", lambda *a, **kw: None)

    task_id = await make_task(test_db)
    await make_participant(test_db, user_id=1, first_name="Loafer", sheet_col=4)

    task = await test_db.get_task_by_id(task_id)
    await _close_deadline(mock_bot, task)
    # имитируем повторный вызов с тем же task-объектом (как если бы был ретрай)
    await _close_deadline(mock_bot, task)

    loafer = await test_db.get_participant(1)
    assert loafer["strikes"] == 1, "повторный close не должен добавлять страйк"


async def test_close_deadline_sends_group_summary(test_db, mock_bot, monkeypatch):
    monkeypatch.setattr(scheduler.sheets, "mark_strike", lambda *a, **kw: None)

    task_id = await make_task(test_db, number=14, title="Valid Palindrome")
    await make_participant(test_db, user_id=1, first_name="Solver", sheet_col=4)
    await make_participant(test_db, user_id=2, first_name="Loafer", sheet_col=5)
    await test_db.mark_done(task_id, 1)

    task = await test_db.get_task_by_id(task_id)
    await _close_deadline(mock_bot, task)

    # первый send_message — итоговый пост в группу
    first_call = mock_bot.send_message.call_args_list[0]
    text = first_call.args[1] if len(first_call.args) > 1 else first_call.kwargs.get("text", "")
    assert "#14" in text
    assert "Valid Palindrome" in text
    assert "Решили (1)" in text
    assert "Страйк (1)" in text


async def test_close_deadline_admin_warn_on_three_strikes(test_db, mock_bot, monkeypatch):
    monkeypatch.setattr(scheduler.sheets, "mark_strike", lambda *a, **kw: None)

    # участник с 2 страйками уже — после этого дедлайна станет 3
    task1_id = await make_task(test_db, number=12)
    task2_id = await make_task(test_db, number=13, status="closed")
    task3_id = await make_task(test_db, number=14, status="closed")
    await make_participant(test_db, user_id=1, first_name="Unlucky", sheet_col=4)
    await test_db.add_strike(1, task2_id)
    await test_db.add_strike(1, task3_id)

    task = await test_db.get_task_by_id(task1_id)
    await _close_deadline(mock_bot, task)

    # два send_message: итог в группу + warn админу
    assert mock_bot.send_message.call_count == 2
    admin_call = mock_bot.send_message.call_args_list[1]
    assert admin_call.args[0] == scheduler.ADMIN_ID
    assert "3 страйка" in (admin_call.args[1] if len(admin_call.args) > 1 else admin_call.kwargs.get("text", ""))


async def test_close_deadline_no_admin_warn_when_below_three(test_db, mock_bot, monkeypatch):
    monkeypatch.setattr(scheduler.sheets, "mark_strike", lambda *a, **kw: None)

    task_id = await make_task(test_db)
    await make_participant(test_db, user_id=1, first_name="Loafer", sheet_col=4)

    task = await test_db.get_task_by_id(task_id)
    await _close_deadline(mock_bot, task)

    # только один вызов — итог в группу, без предупреждения админу
    assert mock_bot.send_message.call_count == 1


# ---------- reminder handlers ----------

async def test_reminder_24h_message_shape(mock_bot):
    task = {"number": 15, "title": "Foo"}
    await _send_reminder_24h(mock_bot, task)

    mock_bot.send_message.assert_called_once()
    text = mock_bot.send_message.call_args.args[1]
    assert "#15" in text and "Foo" in text and "1 день" in text


async def test_reminder_1h_message_shape(mock_bot):
    task = {"number": 15, "title": "Foo"}
    await _send_reminder_1h(mock_bot, task)

    text = mock_bot.send_message.call_args.args[1]
    assert "#15" in text and "Foo" in text and "час" in text
