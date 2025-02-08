from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os

# Загружаем переменные окружения для токена бота
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Инициализация приложения
application = Application.builder().token(TOKEN).build()

# Функция для отправки стартового сообщения с кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Перейти в MiniApp", web_app=WebAppInfo(url='https://gitw1n.github.io/mini-app-test/'))]
    ]

    image_path = r'C:\Users\micro\VSCodeProjects\Python_cybersec_tests\Telegram_Mini_Apps\docs\images\logo.jpg'
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=open(image_path, 'rb'),
        caption='Добро пожаловать в Telesim.tg! Войдите в приложение для продолжения:',
        reply_markup=reply_markup
    )

# Функция для обработки нажатия на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    choice = query.data

    if choice == 'number_1':
        response = "Вы выбрали Виртуальный номер 1. Цена: 10$. Для покупки напишите /buy_1."
    else:
        response = "Неизвестный выбор."

    await query.edit_message_text(text=response)

# Функция для обработки покупки
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    if user_message == '/buy_1':
        response = "Вы успешно приобрели Виртуальный номер 1. Подробности на почте."
    else:
        response = "Для покупки выберите номер через кнопки."

    await update.message.reply_text(response)

# Обработчик неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда. Используйте /start для начала.")

# Основная функция для запуска бота
def main() -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("buy_1", buy))
    application.add_handler(CommandHandler(None, unknown))  # Для неизвестных команд

    application.run_polling()

# Запуск бота
if __name__ == '__main__':
    main()