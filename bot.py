import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import openai
import requests
from io import BytesIO
import config  # импортируем файл конфигурации с токенами

# Логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменная для отслеживания выбора нейросети пользователем
user_network_choice = {}

# Функция для генерации ответа от GPT-4 через API OpenAI
def generate_gpt4_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты бот, который отвечает на вопросы."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error(f"Error with OpenAI API: {e}")
        return "Извините, произошла ошибка при работе с нейросетью."

# Функция для генерации изображения через DALL·E
def generate_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        logger.error(f"Error with OpenAI Image API: {e}")
        return None

# Обработчик команды /start
async def start(update: Update, context):
    user_id = update.message.from_user.id
    user_network_choice[user_id] = 'text'  # По умолчанию нейросеть для текста
    await update.message.reply_text(
        "Привет! Я бот с GPT-4 и DALL·E. Используй команду /set_network чтобы выбрать нейросеть.\n"
        "По умолчанию используется текстовая модель (GPT-4)."
    )

# Обработчик команды для выбора нейросети
async def set_network(update: Update, context):
    user_id = update.message.from_user.id
    if context.args:
        network = context.args[0].lower()
        if network in ['text', 'image']:
            user_network_choice[user_id] = network
            await update.message.reply_text(f"Нейросеть успешно изменена на: {network.upper()}.")
        else:
            await update.message.reply_text("Пожалуйста, выбери 'text' или 'image'.")
    else:
        await update.message.reply_text("Пожалуйста, укажи, какую нейросеть ты хочешь использовать: 'text' или 'image'.")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context):
    user_input = update.message.text
    user_id = update.message.from_user.id
    network_choice = user_network_choice.get(user_id, 'text')

    if network_choice == 'text':
        # Генерация текста через GPT-4
        response = generate_gpt4_response(user_input)
        await update.message.reply_text(response)
    elif network_choice == 'image':
        # Генерация изображения через DALL·E
        image_url = generate_image(user_input)
        if image_url:
            image_data = requests.get(image_url).content
            await update.message.reply_photo(photo=BytesIO(image_data))
        else:
            await update.message.reply_text("Извините, не удалось сгенерировать изображение.")

# Основная функция для запуска бота
async def main():
    # Используй токен, полученный от BotFather
    token = config.TELEGRAM_BOT_API_TOKEN

    app = ApplicationBuilder().token(token).build()

    # Регистрация команд и обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_network", set_network))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    await app.start()
    await app.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())