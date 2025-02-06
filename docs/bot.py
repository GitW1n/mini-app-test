from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os

# Загружаем переменные окружения для токена бота
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

application = Application.builder().token(TOKEN).build()

# Функция для отправки стартового сообщения с кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Создаем кнопки с web_app для MiniApp
    keyboard = [
        [InlineKeyboardButton("Перейти в MiniApp", web_app={'url': 'https://gitw1n.github.io/mini-app-test/'})]  # Ссылка на ваш MiniApp
    ]

    image_path = r'C:\Users\micro\VSCodeProjects\Python_cybersec_tests\Telegram_Mini_Apps\docs\images\logo.jpg'

    # Создаем разметку клавиатуры
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с изображением и кнопками
    await update.message.reply_photo(
        photo=open(image_path, 'rb'), 
        caption='Выберите виртуальный номер для покупки:', 
        reply_markup=reply_markup
    )

# Функция для обработки нажатия на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    # Получаем данные, связанные с кнопкой
    choice = query.data

    if choice == 'number_1':
        response = "Вы выбрали Виртуальный номер 1. Цена: 10$. Для покупки напишите /buy_1."
    else:
        response = "Неизвестный выбор."

    # Отправляем ответ на выбор пользователя
    await query.edit_message_text(text=response)

# Функция для обработки покупки
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    if user_message == '/buy_1':
        response = "Вы успешно приобрели Виртуальный номер 1. Подробности на почте."
    else:
        response = "Для покупки выберите номер через кнопки."

    await update.message.reply_text(response)

# Основная функция для запуска бота
def main() -> None:
    # Строим приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("buy_1", buy))

    # Запускаем бота
    application.run_polling()

# Запуск бота
if __name__ == '__main__':
    main()
