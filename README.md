# Cyberpunk Weather Runner

简单的 Telegram 机器人。

## 功能

- `/run`命令：查询实时 AQI 和是否适合跑步。
- 每天 17:00 向频道发送一条信息，内容为实时 AQI 和是否适合跑步。

## 使用方法

先获得一个[和风天气的 API KEY](https://dev.qweather.com/docs/configuration/project-and-key/)

根目录创建一个 `.env` 文件：
```dotenv
BOT_TOKEN=Telegram机器人的ID
CHAT_ID=机器人每天发送信息的频道的ID，如-1001903027140
WEATHER_API_KEY=和风天气APIKEY
LOCATION=要查询的经纬度，如116.21,39.58
```

运行 `main.py` 即可。
