from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import database as db
import sheets

router = Router()


def _mention(user_id: int, name: str, username: str | None) -> str:
    if username:
        return f"@{username}"
    return f'<a href="tg://user?id={user_id}">{name}</a>'


@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    is_new = await db.register_participant(user.id, user.username, user.first_name)

    if is_new:
        participant = await db.get_participant(user.id)
        try:
            sheets.add_participant_column(user.first_name, participant["sheet_col"])
        except Exception:
            pass
        await message.answer(
            f"✅ Добро пожаловать, {user.first_name}!\n"
            "Ты зарегистрирован в LeetRush.\n\n"
            "Когда решишь задачу — нажми кнопку <b>✅ Решил</b> под постом или напиши /done <номер>.",
            parse_mode="HTML"
        )
    else:
        await message.answer("Ты уже зарегистрирован 👍")


@router.callback_query(F.data.startswith("done:"))
async def callback_done(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    user = callback.from_user

    participant = await db.get_participant(user.id)
    if not participant:
        is_new = await db.register_participant(user.id, user.username, user.first_name)
        if is_new:
            participant = await db.get_participant(user.id)
            try:
                sheets.add_participant_column(user.first_name, participant["sheet_col"])
            except Exception:
                pass
        else:
            participant = await db.get_participant(user.id)

    task = await db.get_active_task()
    if not task or task["id"] != task_id:
        await callback.answer("Эта задача уже закрыта.", show_alert=True)
        return

    already = await db.has_done(task_id, user.id)
    if already:
        await callback.answer("Ты уже отметился ✅", show_alert=True)
        return

    await db.mark_done(task_id, user.id)

    try:
        sheets.mark_cell(task["number"], participant["sheet_col"], done=True)
    except Exception:
        pass

    await callback.answer("✅ Отмечено! Молодец!")


@router.message(Command("done"))
async def cmd_done(message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("Использование: /done <номер задачи>")
        return

    task_number = int(args[1])
    task = await db.get_task_by_number(task_number)
    if not task:
        await message.reply(f"Задача #{task_number} не найдена.")
        return
    if task["status"] == "pending":
        await message.reply(f"Задача #{task_number} ещё не опубликована.")
        return

    user = message.from_user
    participant = await db.get_participant(user.id)
    if not participant:
        is_new = await db.register_participant(user.id, user.username, user.first_name)
        if is_new:
            participant = await db.get_participant(user.id)
            try:
                sheets.add_participant_column(user.first_name, participant["sheet_col"])
            except Exception:
                pass
        else:
            participant = await db.get_participant(user.id)

    already = await db.has_done(task["id"], user.id)
    if already:
        await message.reply(f"Задача #{task_number} уже отмечена ✅")
        return

    await db.mark_done(task["id"], user.id)
    try:
        sheets.mark_cell(task["number"], participant["sheet_col"], done=True)
    except Exception:
        pass

    await message.reply(f"✅ Задача #{task_number} отмечена как выполненная!")


@router.message(Command("undone"))
async def cmd_undone(message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("Использование: /undone <номер задачи>")
        return

    task_number = int(args[1])
    task = await db.get_task_by_number(task_number)
    if not task:
        await message.reply(f"Задача #{task_number} не найдена.")
        return

    user = message.from_user
    participant = await db.get_participant(user.id)
    if not participant:
        await message.reply("Ты не зарегистрирован. Напиши /start.")
        return

    removed = await db.unmark_done(task["id"], user.id)
    if not removed:
        await message.reply(f"Задача #{task_number} не была отмечена.")
        return

    try:
        sheets.mark_cell(task["number"], participant["sheet_col"], done=False)
    except Exception:
        pass

    await message.reply(f"↩️ Отметка по задаче #{task_number} отменена.")
