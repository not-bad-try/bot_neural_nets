import os

import openai
from dotenv import load_dotenv

# Загружаем данные из .env файла
load_dotenv()

# Telegram Bot API токен
TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# OpenAI API ключ
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Устанавливаем OpenAI ключ для библиотеки
openai.api_key = OPENAI_API_KEY