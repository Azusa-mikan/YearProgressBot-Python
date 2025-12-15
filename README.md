# YearProgressBot

A Python-based Telegram year progress bot, rewritten from [RedL0tus/YearProgressBot](https://github.com/RedL0tus/YearProgressBot).

*The prime of life never returns, one morning is hard to come again. Seize the day and encourage yourself, time and tide wait for no man. — Tao Yuanming*

[中文文档](README_zh.md)

## Features

- 📊 Display current year progress percentage
- ⏰ Send daily progress updates at a fixed time
- 🔄 Auto-detect progress changes and only push when the progress bar changes to avoid spamming
- 📱 Broadcast to multiple chat IDs
- 🌍 Custom timezone support (e.g. `Asia/Shanghai`)
- 📏 Configurable progress bar length

## Installation

The project requires Python 3.12 or higher.

Install dependencies with `pip`:

```bash
pip install -r requirements.txt
```

Or, using a tool that understands `pyproject.toml` (for example `uv`):

```bash
uv sync
```

## Environment Configuration

Create a `.env` file in the project root and configure the following environment variables:

```env
TELEGRAM_TOKEN=Your Telegram bot token (required)
TELEGRAM_CHAT_ID=Your chat ID (multiple IDs separated by commas, optional)
TELEGRAM_ADMIN_ID=User ID that can use admin commands (optional, recommended)
TZ=Timezone (optional, e.g. Asia/Shanghai)
SCHEDULE_TIME=Scheduled sending time (optional, format HH:MM, 24-hour)
PROGRESS_BAR_LENGTH=Progress bar length (optional, default 20)
```

Notes:

- If `TELEGRAM_CHAT_ID` is not set, the bot will not auto-push messages and you can only query progress interactively.
- If `TZ` is not set or is invalid, the bot falls back to the system local timezone.
- If `SCHEDULE_TIME` is not set or invalid, the bot automatically switches to “auto-detection mode” based on progress changes.

## Usage

### Start the bot

In the project root, run:

```bash
python main.py
```

After startup, the bot will:

- Periodically check or send year progress based on your configuration
- Continuously poll Telegram updates and respond to commands

## Bot Commands

- `/status`  
  Show the current time and year progress, and indicate how the next automatic send will be triggered:
  - If `SCHEDULE_TIME` is configured, it shows the next fixed send time
  - Otherwise, it shows “send when progress increases by 1%”

- `/test`  
  Test whether message sending works:
  - If `TELEGRAM_ADMIN_ID` is configured, only that user can use this command
  - Unauthorized users will receive a “not authorized” message

## Operation Modes

### 1. Scheduled Mode (time-based)

When a valid `SCHEDULE_TIME` (for example `09:00`) is set, the bot will:

- Send one year progress message (with two decimal places) every day at the specified time
- Use the configured `TZ` for time calculation; if not set, the system local timezone is used

### 2. Auto-detection Mode (progress-based)

When `SCHEDULE_TIME` is not set or is invalid, the bot switches to auto-detection mode:

- It checks the current year progress at a fixed interval (default every 100 seconds)
- A message is only sent when the textual progress bar differs from the last one
- This effectively avoids sending duplicate messages in a short period

## Technical Details

- Use `pytelegrambotapi` to interact with the Telegram Bot API
- Use `apscheduler` to manage scheduled jobs (interval-based and daily cron triggers)
- Use `python-dotenv` for environment variable management
- Use `pytz` for timezone handling
- Use `aiohttp` as the underlying HTTP client (required by async pytelegrambotapi)

## Differences from the Original Version

- 🔄 Rewritten from a Bash script into a Python implementation
- 🧠 Local cache to only push when the progress bar changes, reducing noise
- 🛡️ Additional configuration validation and logging for better robustness
- 🔧 Support for multiple chat IDs, configurable progress bar length, and custom timezones

## License

This project is based on the original [WTFNMFPLv1](https://github.com/RedL0tus/YearProgressBot/blob/master/LICENSE) license.

## Contributing

Issues and Pull Requests are welcome!
