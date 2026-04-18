# LeetRush Bot

Telegram bot for automating a group LeetCode challenge.

## Stack
- Python 3.12 + aiogram 3.15.0
- aiosqlite (SQLite at `data/leetrush.db`)
- gspread + google-auth (Google Sheets sync)
- APScheduler (reminders + deadline processing)
- Docker + Coolify (deployment)

## Key config
- `ADMIN_ID`: 215949956 (Амади)
- `GROUP_ID`: -1003526184369
- `TASK_START_NUMBER`: 12 (first task number)
- Coolify app UUID: `zgk800oo44csc8kgk4coc0gc`
- Persistent volume: `/root/leetrush-data` → `/app/data`
- Google credentials: stored as `GOOGLE_CREDENTIALS_BASE64` env var in Coolify, decoded to `credentials.json` at bot startup
- Google Sheet GID: `1112096595`

## Sheet layout
- Row 1: headers — `№ | Задача | Дедлайн | [participant names...]`
- Rows 2+: tasks starting from #12 (`row = 2 + (task_number - 12)`)
- Participant columns are 0-based; matched by `first_name` via `sheets.find_col_by_name()`

## Current participants in DB
| sheet_col | first_name | username |
|-----------|------------|----------|
| 4 | Амади | @amady |
| 5 | Джамбек | @donflamingo |
| 7 | Александр | @Alek000sandr |
| 8 | Felix Youssoupoff | — |
| 9 | шейхуль голанг | — |
| 10 | Tamirlan | @txmrln |
| 11 | K1la | @k1laof |
| 12 | ? | — |
| 13 | Dzhambulat | @jambulatw |
| 14 | 🧠☠️ Хамзат Эчилов | — |

Not yet registered (need to /start): Gamzat (col 6), @okk_otsu, @janaridevv, @as_suguri, @monotheistx, @themisar

## Task pool
Tasks #12–#21, Two Pointers theme. #12 (Reverse String) currently active, deadline 07.04.2026 23:59 MSK.

## Deployment
Push to `main` → manually trigger redeploy in Coolify (no auto-deploy webhook configured).
Or use: `mcp__coolify__deploy` with uuid `zgk800oo44csc8kgk4coc0gc`

## Admin commands
- `/next 3d` or `/next 08.04.2026 23:59` — publish next task
- `/status` — task progress (available to all users after PR #1)
- `/strikes` — strike table
- `/tasks` — pending task queue
- `/kick @username` or `/kick USER_ID` — ban from group

## User commands
- `/start` — register
- `/done N` — mark task N complete
- `/undone N` — unmark
- `/status` — see who solved current task

## Scheduler
Single runner `run_jobs` ticks every 5 min. Reads `scheduled_jobs` table: `SELECT WHERE status='pending' AND fire_at <= now()`, dispatches by `kind` (`reminder_24h`, `reminder_1h`, `close_deadline`), marks `done`/`failed`. Jobs are inserted at `/next` time with `deadline - 24h`, `deadline - 1h`, `deadline`; past fire_ats are skipped. Closed tasks cause pending jobs to be silently marked done.
