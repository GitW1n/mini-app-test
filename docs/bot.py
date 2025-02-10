from fastapi import FastAPI
from pydantic import BaseModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import os
import uvicorn
from threading import Thread

# Загружаем переменные окружения для токена бота
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Инициализация приложения FastAPI
app = FastAPI()

# Словарь для хранения баланса пользователей
user_balances = {}

# Модель для обновления баланса
class BalanceUpdate(BaseModel):
    user_id: int
    balance: int

# Функция для сохранения баланса (заглушка для примера)
def save_user_balances(balances):
    pass

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

# Функция для отправки стартового сообщения с кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.first_name

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

# Добавляем защиту для команд, доступных только администратору
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

# Функция для обработки неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

# Основная функция для запуска бота
def main() -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))  # Команда для просмотра баланса
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))  # Обработка неизвестных команд

    application.run_polling()

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
ч