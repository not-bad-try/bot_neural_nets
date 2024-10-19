import time
import datetime
from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes
import config

# Словарь для хранения информации о подписках пользователей
user_subscriptions = {}

# Различные варианты подписки с ценами (в копейках или центах)
subscription_plans = {
    "day": {"duration": 1, "price": 1000},      # 10 рублей
    "week": {"duration": 7, "price": 5000},     # 50 рублей
    "month": {"duration": 30, "price": 15000},  # 150 рублей
    "year": {"duration": 365, "price": 100000}, # 1000 рублей
    "forever": {"duration": None, "price": 500000}  # 5000 рублей
}

# Проверяем, есть ли активная подписка у пользователя.
def has_active_subscription(user_id):
    if user_id in user_subscriptions:
        expiration_time = user_subscriptions[user_id]
        if expiration_time is None:
            return True  # Подписка "навсегда"
        return time.time() < expiration_time  # Сравниваем текущее время с временем истечения подписки
    return False

# Добавляем подписку пользователю на заданный период.
def add_subscription(user_id, duration):
    if duration is None:  # Подписка "навсегда"
        user_subscriptions[user_id] = None
    else:
        expiration_time = time.time() + (duration * 24 * 60 * 60)  # Время истечения подписки
        user_subscriptions[user_id] = expiration_time

# Сообщаем пользователю статус подписки.
async def subscription_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if has_active_subscription(user_id):
        expiration_time = user_subscriptions.get(user_id)
        if expiration_time is None:
            await update.message.reply_text("У вас подписка на 'навсегда'.")
        else:
            expiration_date = datetime.datetime.fromtimestamp(expiration_time).strftime('%Y-%m-%d %H:%M:%S')
            await update.message.reply_text(f"Ваша подписка активна до {expiration_date}.")
    else:
        await update.message.reply_text("У вас нет активной подписки. Пожалуйста, оформите подписку.")

# Оформляем подписку на выбранный план.
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.args:
        plan = context.args[0].lower()
        if plan in subscription_plans:
            # Формирование счета для оплаты
            title = f"Подписка на {plan}"
            description = f"Подписка на {plan} предоставляет вам доступ к боту на {plan}."
            prices = [LabeledPrice(f"Подписка на {plan}", subscription_plans[plan]["price"])]
            
            # Отправляем счет пользователю
            await context.bot.send_invoice(
                chat_id=user_id,
                title=title,
                description=description,
                payload=f"subscription-{plan}",
                provider_token=config.PAYMENT_PROVIDER_TOKEN,
                currency="RUB",  # Валюта (может быть "USD" для долларов)
                prices=prices,
                start_parameter="subscription",
                is_flexible=False  # Цена фиксирована
            )
        else:
            await update.message.reply_text("Пожалуйста, выберите правильный план подписки: day, week, month, year, forever.")
    else:
        await update.message.reply_text("Пожалуйста, укажите план подписки: day, week, month, year, forever.")

# Обработчик успешной оплаты
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    invoice_payload = update.message.successful_payment.invoice_payload
    plan = invoice_payload.split("-")[1]  # Получаем название плана из payload
    
    duration = subscription_plans[plan]["duration"]
    add_subscription(user_id, duration)
    await update.message.reply_text(f"Ваш платеж на {plan} успешно обработан! Подписка активирована.")
