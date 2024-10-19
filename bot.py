import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, PreCheckoutQueryHandler, filters
import openai
import requests
from io import BytesIO
import config
from subscription import has_active_subscription, subscription_status, subscribe, successful_payment  # Функции для работы с подписками

# Логирование
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
        "По умолчанию используется текстовая модель (GPT-4).\n"
        "Чтобы узнать статус подписки, используй команду /subscription_status.\n"
        "Чтобы оформить подписку, используй команду /subscribe <plan>, где <plan> может быть 'day', 'week', 'month', 'year', 'forever'."
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
    user_id = update.message.from_user.id
    # Проверка подписки
    if not has_active_subscription(user_id):
        await update.message.reply_text("У вас нет активной подписки. Пожалуйста, оформите подписку.")
        return
    
    user_input = update.message.text
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

# Обработчик предоплаты
async def precheckout_callback(update: Update, context):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith('subscription-'):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Произошла ошибка с заказом. Попробуйте снова.")

# Основная функция для запуска бота
async def main():
    token = config.TELEGRAM_BOT_API_TOKEN

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_network", set_network))
    app.add_handler(CommandHandler("subscription_status", subscription_status))  # Статус подписки
    app.add_handler(CommandHandler("subscribe", subscribe))  # Оформление подписки
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))  # Обработчик предоплаты
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))  # Обработчик успешной оплаты


    await app.start()
    await app.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
