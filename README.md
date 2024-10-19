# Telegram GPT-4 и DALL·E бот с платной подпиской

Этот бот позволяет пользователям взаимодействовать с нейросетями GPT-4 и DALL·E для генерации текстов и изображений, а также поддерживает оплату подписки через Telegram.

## Функционал

- Генерация текстовых ответов с помощью GPT-4.
- Генерация изображений с помощью DALL·E.
- Платная подписка с вариантами на день, неделю, месяц, год или навсегда.

## Установка и запуск

### Шаги:

1. Клонируйте репозиторий и перейдите в директорию проекта:
    ```
    git clone <repository-url>
    cd telegram-gpt4-bot
    ```

2. Установите необходимые зависимости:
    ```
    pip install -r requirements.txt
    ```

3. Создайте `.env` файл и добавьте в него токен Telegram API и OpenAI API:
    ```
    TELEGRAM_BOT_API_TOKEN=<Ваш токен бота>
    OPENAI_API_KEY=<Ваш API-ключ OpenAI>
    PAYMENT_PROVIDER_TOKEN=<Токен платежного провайдера>
    ```

4. Запустите бота:
    ```
    python bot.py
    ```

5. Пользователи смогут выбрать план подписки, используя команду `/subscribe <plan>`, где `<plan>` может быть `day`, `week`, `month`, `year`, `forever`. Бот отправит счет на оплату, и после успешной транзакции подписка будет активирована.

## Автор
Лычев Егор - [GitHub](https://github.com/not-bad-try)