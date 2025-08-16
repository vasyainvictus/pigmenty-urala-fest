# routes/auth.py - ФИНАЛЬНАЯ ВЕРСИЯ

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from extensions import db
from flask_login import login_user, logout_user, current_user, login_required
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Мы возвращаем наш разрыватель цикла, теперь он будет работать корректно
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        user_code = request.form.get('code')
        user = User.query.filter_by(code=user_code).first()

        if user:
            # Генерация и сохранение токена в БД - все правильно
            new_token = secrets.token_hex(32)
            user.session_token = new_token
            db.session.commit()
            
            # === КЛЮЧЕВОЕ ИЗМЕНЕНИЕ ПОРЯДКА ===
            # 1. Мы сначала вызываем login_user().
            #    Эта функция создает защищенную сессию и записывает в нее user_id.
            login_user(user)
            
            # 2. И только ПОТОМ, в уже созданную сессию, мы добавляем наш токен.
            #    Это гарантирует, что он будет корректно сохранен.
            session['session_token'] = new_token
            # === КОНЕЦ ИЗМЕНЕНИЯ ===

            flash('Вход выполнен успешно!', 'success')
            
            # Теперь, когда сессия создана ПРАВИЛЬНО, редирект на дашборд будет работать
            return redirect(url_for('main.dashboard'))
        else:
            flash('Неверный код доступа. Попробуйте еще раз.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    # Эта функция уже была написана правильно
    if current_user.is_authenticated:
        current_user.session_token = None
        db.session.commit()
    
    logout_user()
    session.clear()

    flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('auth.login'))