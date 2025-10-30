# YearProgressBot

一个基于Python重构的Telegram年度进度机器人，根据 [RedL0tus/YearProgressBot](https://github.com/RedL0tus/YearProgressBot) 重构而来。

*盛年不重来，一日难再晨。及时当勉励，岁月不待人。 ——陶渊明*

## 功能特性

- 📊 显示当前年份的进度百分比
- ⏰ 支持定时发送进度更新
- 🔄 自动检测进度变化，避免重复发送
- 📱 支持多个聊天ID
- 🌍 支持自定义时区
- 📏 可配置进度条长度

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

创建 `.env` 文件并配置以下环境变量：

```env
TELEGRAM_TOKEN=你的Telegram机器人令牌
TELEGRAM_CHAT_ID=你的聊天ID（多个用逗号分隔）
TZ=时区（可选，如 Asia/Shanghai）
SCHEDULE_TIME=定时发送时间（可选，格式 HH:MM）
PROGRESS_BAR_LENGTH=进度条长度（可选，默认20）
```

## 使用方法

### 启动机器人

```bash
python main.py
```

### 机器人命令

- `/status` - 查看当前年份进度
- `/test` - 测试发送消息

## 运行模式

### 定时模式
当设置了 `SCHEDULE_TIME` 时，机器人会在指定时间发送进度更新。

### 自动检测模式
当未设置 `SCHEDULE_TIME` 时，机器人会自动检测进度变化，当进度百分比增加1%时发送更新。

## 技术实现

- 使用 `python-telegram-bot` 库处理Telegram API
- 使用 `python-dotenv` 管理环境变量
- 使用 `pytz` 处理时区
- 使用 `schedule` 库处理定时任务
- 使用多线程处理机器人轮询和进度检查

## 与原版区别

- 🔄 从Bash脚本重构为Python实现
- 🛠️ 更健壮的错误处理和日志记录
- 🔧 更灵活的配置选项

## 许可证

本项目基于原版 [WTFNMFPLv1](https://github.com/RedL0tus/YearProgressBot/blob/master/LICENSE) 许可证。

## 贡献

欢迎提交Issue和Pull Request！