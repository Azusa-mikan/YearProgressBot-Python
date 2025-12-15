# YearProgressBot

一个基于 Python 的 Telegram 年度进度机器人，根据 [RedL0tus/YearProgressBot](https://github.com/RedL0tus/YearProgressBot) 重写而来。

*盛年不重来，一日难再晨。及时当勉励，岁月不待人。 ——陶渊明*

## 功能特性

- 📊 显示当前年份的进度百分比
- ⏰ 支持每日定时发送进度更新
- 🔄 支持按进度变化自动发送，只在进度条变化时推送，避免刷屏
- 📱 支持多个聊天 ID 群发
- 🌍 支持自定义时区（例如 `Asia/Shanghai`）
- 📏 可配置进度条长度

## 安装依赖

项目需要 Python 3.12 及以上版本。

使用 `pip` 安装依赖：

```bash
pip install -r requirements.txt
```

或使用支持 `pyproject.toml` 的工具（如 `uv` 等）安装：

```bash
uv sync
```

## 环境配置

在项目根目录创建 `.env` 文件并配置以下环境变量：

```env
TELEGRAM_TOKEN=你的Telegram机器人令牌（必填）
TELEGRAM_CHAT_ID=你的聊天ID（多个用逗号分隔，可选）
TELEGRAM_ADMIN_ID=拥有管理命令权限的用户ID（可选，推荐配置）
TZ=时区（可选，如 Asia/Shanghai）
SCHEDULE_TIME=定时发送时间（可选，格式 HH:MM，24 小时制）
PROGRESS_BAR_LENGTH=进度条长度（可选，默认 20）
```

说明：

- 若未配置 `TELEGRAM_CHAT_ID`，机器人不会自动推送，只能在对话中手动查看进度。
- 若未配置 `TZ` 或配置为非法值，将回退为系统本地时区。
- 若未配置或错误配置 `SCHEDULE_TIME`，将自动启用“按进度变化自动发送”模式。

## 使用方法

### 启动机器人

在项目根目录执行：

```bash
python main.py
```

启动后机器人会：

- 按配置的模式定期检查或发送年度进度
- 持续轮询 Telegram 消息，响应命令

## 机器人命令

- `/status`  
  显示当前时间和年份进度，并提示下一次自动发送的触发方式：
  - 若配置了 `SCHEDULE_TIME`，显示下一次发送的固定时间
  - 否则显示“当进度增加 1% 时发送”

- `/test`  
  测试消息发送是否正常：
  - 若配置了 `TELEGRAM_ADMIN_ID`，只有该用户可以使用此命令
  - 未授权用户会收到“无权限使用此命令”的提示

## 运行模式

### 1. 定时模式（按时间发送）

当设置了合法的 `SCHEDULE_TIME`（例如 `09:00`）时，机器人会：

- 每天在指定时间发送一条当前年份进度消息（带两位小数）
- 使用配置的 `TZ` 时区计算时间；若未配置则使用系统本地时区

### 2. 自动检测模式（按进度变化发送）

当未设置 `SCHEDULE_TIME`，或配置值不合法时，机器人会进入自动检测模式：

- 每隔固定时间检查一次当前年份进度（默认每 100 秒）
- 仅当进度条文本相较上次发生变化时才发送消息
- 有效避免在短时间内重复推送相同内容

## 技术实现

- 使用 `pytelegrambotapi` 提供的 Telegram Bot 能力
- 使用 `apscheduler` 管理定时任务（支持按间隔和按每日时间触发）
- 使用 `python-dotenv` 加载和管理环境变量
- 使用 `pytz` 处理时区
- 使用 `aiohttp` 作为底层 HTTP 客户端（异步 pytelegrambotapi 需要）

## 与原版区别

- 🔄 从 Bash 脚本重写为 Python 实现
- 🧠 增加本地缓存文件，只在进度条变化时推送消息，避免刷屏
- �️ 增加多项配置校验与错误日志，提升稳定性
- 🔧 支持多聊天 ID、可配置进度条长度、自定义时区等特性

## 许可证

本项目基于原版 [WTFNMFPLv1](https://github.com/RedL0tus/YearProgressBot/blob/master/LICENSE) 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！
