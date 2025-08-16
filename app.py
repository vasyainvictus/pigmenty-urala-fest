# app.py
# Основной файл Flask-приложения с использованием паттерна Application Factory

from flask import Flask, session
from config import Config
# 1. Импортируем login_manager из extensions.py
from extensions import db, migrate, login_manager 
# Модели User и другие здесь больше не нужны для глобального контекста
from models import User 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Глобальный словарь категорий (для отображения во всех шаблонах) ---
    @app.context_processor
    def inject_display_maps():
        CATEGORY_MAP = {
            'healed': 'Зажившая',
            'fresh': 'Битва',
            'both': 'ПЮ',
            'pro': 'Про',
            'junior': 'Юниор',
            'participant': 'Участник',
            'judge': 'Судья',
            'admin': 'Администратор'
        }
        return dict(CATEGORY_MAP=CATEGORY_MAP)

    # 2. УДАЛЯЕМ старый обработчик контекста inject_user()
    #    @app.context_processor
    #    def inject_user():
    #        ...
    #    Flask-Login автоматически предоставляет переменную `current_user`
    #    во всех шаблонах, поэтому этот код больше не нужен.
    #    В ваших шаблонах (base.html и т.д.) просто используйте `current_user` вместо `user`.
    #    Например, `{% if current_user.is_authenticated %}` вместо `{% if user %}`.

    # --- Инициализация расширений ---
    db.init_app(app)
    migrate.init_app(app, db)
    # 3. ИНИЦИАЛИЗИРУЕМ LoginManager
    login_manager.init_app(app)

    # --- Регистрация Blueprints ---
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app