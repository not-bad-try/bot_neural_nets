import os
from dotenv import load_dotenv

# Загружаем данные из .env файла
load_dotenv()

# Telegram Bot API токен
TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# OpenAI API ключ
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Telegram Payment Token для работы с платежами (например, Stripe)
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")

# Устанавливаем OpenAI ключ для библиотеки
openai.api_key = OPENAI_API_KEY
