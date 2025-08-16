# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import session
import datetime # Импортируем для вывода времени в логах

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.login_message = "Для доступа к этой странице необходимо войти в систему."
login_manager.login_message_category = "error"

@login_manager.user_loader
def load_user(user_id):
    """
    Функция с подробным логированием для отладки цикла переадресации.
    """
    from models.user import User
    
    # Получаем текущее время для лога
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"--- [{timestamp}] user_loader вызван для user_id: {user_id} ---")

    user = User.query.get(int(user_id))

    if not user:
        print(">>> РЕЗУЛЬТАТ: Пользователь не найден в БД. Сессия невалидна.")
        return None

    # Получаем токены
    token_from_db = user.session_token
    token_from_session = session.get('session_token')

    print(f"  - Токен в базе данных: {token_from_db}")
    print(f"  - Токен в сессии:      {token_from_session}")

    # Надежная проверка
    if token_from_db is not None and token_from_db == token_from_session:
        print(">>> РЕЗУЛЬТАТ: Токены существуют и совпадают. Сессия ВАЛИДНА.")
        return user
    else:
        print(">>> РЕЗУЛЬТАТ: Токены НЕ совпадают или один из них пуст. Сессия НЕВАЛИДНА.")
        return None