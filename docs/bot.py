import os
import json
from threading import Thread
from fastapi import FastAPI
from pydantic import BaseModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import subprocess
import uvicorn
from datetime import datetime
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info("Бот запущен")



load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Инициализация приложения FastAPI
app = FastAPI()

# Словарь для хранения баланса пользователей
user_balances = {}

current_time = datetime.now()

# Модель для обновления баланса
class BalanceUpdate(BaseModel):
    user_id: int
    balance: int

# Функция для сохранения баланса в файл
def save_user_balances(balances):
    with open("balances.json", "w") as f:
        json.dump(balances, f)

# Функция для загрузки балансов из файла
def load_user_balances():
    try:
        with open("balances.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Загрузка балансов при запуске
user_balances = load_user_balances()

@app.post("/update_balance")
async def update_balance(update: BalanceUpdate):
    user_id = update.user_id
    new_balance = update.balance

    # Обновляем баланс пользователя
    user_balances[user_id] = new_balance
    save_user_balances(user_balances)  # Сохраняем данные

    return {"status": "success", "new_balance": new_balance}

# Инициализация приложения Telegram
application = Application.builder().token(TOKEN).build()

user_last_start = {}  # Словарь для хранения времени последнего старта для каждого пользователя


# Функция для отправки стартового сообщения с кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.first_name

    user_last_start[user_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Записываем время последнего старта
    last_start = user_last_start.get(user_id, "Неизвестно")


    # Инициализация баланса, если пользователь запускает впервые
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Баланс по умолчанию = 0

    balance = user_balances[user_id]

    keyboard = [
        [InlineKeyboardButton("Перейти в MiniApp", web_app={"url": "https://gitw1n.github.io/mini-app-test/"})],
        [InlineKeyboardButton("Проверить баланс (Можно по команде /balance)", callback_data='check_balance')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f'Добро пожаловать, {username}!\nВаш текущий баланс: {balance}₽'

    await update.message.reply_text(
        text=text,
        reply_markup=reply_markup
    )

# Функция для обработки нажатия на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == 'check_balance':
        user_id = update.effective_user.id
        balance = user_balances.get(user_id, 0)
        response = f"Ваш текущий баланс: 💰 {balance}₽"
    else:
        response = "Неизвестный выбор."

    await query.edit_message_text(text=response)

# 📥 Команда для проверки баланса
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    balance = user_balances.get(user_id, 0)
    await update.message.reply_text(f"Ваш текущий баланс: 💰 {balance}₽")

# Защита для команд, доступных только администратору
ADMIN_USER_ID = 1024171288  # Замените на ваш Telegram ID

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    if not user_balances:
        await update.message.reply_text("Нет пользователей.")
        return

    # Составляем список пользователей
    users_list = "\n".join([f"User ID: {user_id}, Balance: {balance}₽" 
                            for user_id, balance in user_balances.items()])
    
    await update.message.reply_text(f"Список пользователей:\n{users_list}")

application.add_handler(CommandHandler("users", users))

# 📥 Команда для пополнения баланса
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    try:
        # Проверяем, указал ли пользователь сумму
        amount = int(context.args[0])
        if amount <= 0:
            await update.message.reply_text("Пожалуйста, укажите сумму больше 0.")
            return

        # Обновляем баланс пользователя
        user_balances[user_id] = user_balances.get(user_id, 0) + amount
        save_user_balances(user_balances)  # Сохраняем данные

        await update.message.reply_text(f"Баланс успешно пополнен на {amount}₽. Новый баланс: 💰 {user_balances[user_id]}₽")

    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, используйте команду в формате: /add_balance <сумма>")


# current_time = datetime.now() находится выше на первых строках, примерно 20-40 строка

async def time(update: Update , context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id


    await update.message.reply_text(f"Текущее время:{current_time}")

 
async def security(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id  # Получаем ID пользователя

    # Получаем время последнего старта для данного пользователя
    last_start = user_last_start.get(user_id, "Неизвестно")

    # Отправляем сообщение с данными пользователя и клавиатурой
    await update.message.reply_text(f"""
    Безопасность 🛡️
    Ваш ID: {user_id}
    Последний вход: {last_start}
    """)

    # Создание клавиатуры с кнопками
    security_keyboard = [
        [InlineKeyboardButton("Личная Информация 🛡️", callback_data='security')],
        [InlineKeyboardButton(f"Последний вход 🛡️: {last_start}", callback_data='last_start')]
    ]
    
    reply_markup = InlineKeyboardMarkup(security_keyboard)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id  # Получаем ID пользователя

    # Отправляем сообщение с настройками
    await update.message.reply_text(f"""
    Настройки ⚙️
    Ваш ID: {user_id}
    """)

    # Клавиатура с настройками
    settings_keyboard = [
        [InlineKeyboardButton("Перейти в MiniApp для настройки конфигурации стиля", web_app={"url": "https://gitw1n.github.io/mini-app-test/"})],
        [InlineKeyboardButton("Безопасность 🛡️", callback_data='security')]
    ]
    
    reply_markup = InlineKeyboardMarkup(settings_keyboard)
    await update.message.reply_text("Выберите настройку:", reply_markup=reply_markup)


# 📥 Команда для выполнения ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        result = subprocess.run(["ping", "-c", "4", "8.8.8.8"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            await update.message.reply_text(f"Результат ping:\n{result.stdout}")
        else:
            await update.message.reply_text(f"Ошибка при выполнении ping:\n{result.stderr}")

    except subprocess.TimeoutExpired:
        await update.message.reply_text("Время ожидания ответа истекло.")

# Регистрация команды
application.add_handler(CommandHandler("ping", ping))

# Функция для обработки неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

# Основная функция для запуска бота
def main() -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))  # Команда для просмотра баланса
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("add_balance", add_balance)) 
    application.add_handler(CommandHandler("time", time)) 
    application.add_handler(CommandHandler("security", security)) 
    application.add_handler(CommandHandler("settings", settings)) 
    application.add_handler(MessageHandler(filters.COMMAND, unknown))  # Обработка неизвестных команд

    application.run_polling()

# API для пополнения баланса через FastAPI
@app.post("/add_balance")
async def add_balance_api(update: BalanceUpdate):
    user_id = update.user_id
    amount = update.balance

    if amount <= 0:
        return {"status": "error", "message": "Сумма должна быть больше 0."}

    # Пополнение баланса
    user_balances[user_id] = user_balances.get(user_id, 0) + amount
    save_user_balances(user_balances)  # Сохраняем данные

    return {"status": "success", "new_balance": user_balances[user_id]}

# Функция для запуска FastAPI сервера
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Запуск бота и FastAPI в разных потоках
if __name__ == "__main__":
    # Запуск FastAPI сервера в отдельном потоке
    thread = Thread(target=run_fastapi)
    thread.start()

    # Запуск Telegram бота
    main()
