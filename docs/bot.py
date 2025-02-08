from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import MessageHandler, filters
from dotenv import load_dotenv
import os

# Загружаем переменные окружения для токена бота
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Инициализация приложения
application = Application.builder().token(TOKEN).build()

# 🗂️ Словарь для хранения баланса пользователей
user_balances = {}

# Функция для отправки стартового сообщения с кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.first_name

    # Инициализация баланса, если пользователь запускает впервые
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Баланс по умолчанию = 0

    balance = user_balances[user_id]

    keyboard = [
        [InlineKeyboardButton("Перейти в MiniApp", web_app=WebAppInfo(url='https://gitw1n.github.io/mini-app-test/'))]
    [InlineKeyboardButton("Проверить баланс (Можно по команде /balance)", callback_data='check_balance')]
    ]
    image_path = r'C:\Users\micro\VSCodeProjects\Python_cybersec_tests\Telegram_Mini_Apps\docs\images\logo.jpg'
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 👤 Отображаем имя пользователя и баланс
    caption = f'Добро пожаловать, {username} 💰 {balance}₽!\nВойдите в приложение для продолжения:'

    await update.message.reply_photo(
        photo=open(image_path, 'rb'),
        caption=caption,
        reply_markup=reply_markup
    )

# Функция для обработки нажатия на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    choice = query.data

    if choice == 'number_1':
        response = "Вы выбрали Виртуальный номер 1. Цена: 10$. Для покупки напишите /buy_1."
    elif choice == 'check_balance':
        response = f"Ваш текущий баланс: 💰 {balance}₽"
    else:
        response = "Неизвестный выбор."

    await query.edit_message_text(text=response)

# Функция для обработки покупки
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_message == '/buy_1':
        # Проверяем, хватает ли баланса
        if user_balances.get(user_id, 0) >= 10:
            user_balances[user_id] -= 10  # Списываем 10₽
            response = "Вы успешно приобрели Виртуальный номер 1. Подробности на почте."
        else:
            response = "Недостаточно средств на балансе. Пополните баланс, чтобы совершить покупку."
    else:
        response = "Для покупки выберите номер через кнопки."

    await update.message.reply_text(response)

# 📥 Команда для проверки баланса
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    balance = user_balances.get(user_id, 0)
    await update.message.reply_text(f"Ваш текущий баланс: 💰 {balance}₽")

# Обработчик неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

# Основная функция для запуска бота
def main() -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))  # Команда для просмотра баланса
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("buy_1", buy))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))  # Обработка неизвестных команд

    application.run_polling()

# Запуск бота
if __name__ == '__main__':
    main()
