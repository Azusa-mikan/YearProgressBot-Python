# YearProgressBot

A Python-based Telegram year progress bot, refactored from [RedL0tus/YearProgressBot](https://github.com/RedL0tus/YearProgressBot).

*The prime of life never returns, one morning is hard to come again. Seize the day and encourage yourself, time and tide wait for no man. — Tao Yuanming*

## Features

- 📊 Display current year progress percentage
- ⏰ Support scheduled progress updates
- 🔄 Automatic progress change detection to avoid duplicate sending
- 📱 Support multiple chat IDs
- 🌍 Support custom timezone
- 📏 Configurable progress bar length

## Installation

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file and configure the following environment variables:

```env
TELEGRAM_TOKEN=Your Telegram bot token
TELEGRAM_CHAT_ID=Your chat ID (multiple IDs separated by commas)
TZ=Timezone (optional, e.g. Asia/Shanghai)
SCHEDULE_TIME=Scheduled sending time (optional, format HH:MM)
PROGRESS_BAR_LENGTH=Progress bar length (optional, default 20)
```

## Usage

### Start the Bot

```bash
python main.py
```

### Bot Commands

- `/status` - Check current year progress
- `/test` - Test sending messages

## Operation Modes

### Scheduled Mode
When `SCHEDULE_TIME` is set, the bot will send progress updates at the specified time.

### Auto-detection Mode
When `SCHEDULE_TIME` is not set, the bot will automatically detect progress changes and send updates when the progress percentage increases by 1%.

## Technical Implementation

- Use `python-telegram-bot` library for Telegram API
- Use `python-dotenv` for environment variable management
- Use `pytz` for timezone handling
- Use `schedule` library for scheduled tasks
- Use multi-threading for bot polling and progress checking

## Differences from Original Version

- 🔄 Refactored from Bash script to Python implementation
- 🛠️ More robust error handling and logging
- 🔧 More flexible configuration options

## License

This project is based on the original [WTFNMFPLv1](https://github.com/RedL0tus/YearProgressBot/blob/master/LICENSE) license.

## Contributing

Welcome to submit Issues and Pull Requests!