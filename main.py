import os
from datetime import time, timezone, timedelta

import requests
from dotenv import load_dotenv
import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
LOCATION = os.getenv('LOCATION')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help, Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def get_weather_aqi() -> int:
    url = 'https://devapi.qweather.com/v7/air/now'
    params = {'location': LOCATION, 'key': WEATHER_API_KEY, 'lang': 'zh-hans'}
    headers = {'Accept-Encoding': 'gzip, deflate'}

    aqi = -1
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise exception if the request was unsuccessful
        data = response.json()
        aqi = int(data.get('now', {}).get('aqi', -1))  # Use get() method to avoid KeyError
    except requests.exceptions.RequestException as err:
        logger.error(err)

    return aqi


async def check_weather_condition() -> str:
    aqi = await get_weather_aqi()
    if aqi == -1:
        return 'Sorry, server error!'
    elif aqi <= 75:
        return 'AQI is ' + str(aqi) + '. Run!'
    else:
        return 'AQI is ' + str(aqi) + '. No run!'


async def check_weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = await check_weather_condition()
    await update.message.reply_text(result)


async def check_weather_callback(context: ContextTypes.DEFAULT_TYPE):
    result = await check_weather_condition()
    await context.bot.send_message(chat_id=CHAT_ID, text=result)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("run", check_weather_command))

    # on non command i.e. message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    job_queue = application.job_queue
    tz = timezone(timedelta(hours=8))  # UTC+8 timezone
    job_check_weather_condition = job_queue.run_daily(check_weather_callback,
                                                      time=time(hour=17, minute=0, tzinfo=tz))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


async def test_weather():
    result = await check_weather_condition()
    print(result)


if __name__ == "__main__":
    main()
