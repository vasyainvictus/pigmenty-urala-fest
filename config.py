# config.py

# 1. Импортируем библиотеку 'os' для работы с путями к файлам
import os

# 2. Определяем базовый каталог проекта.
#    os.path.dirname(__file__) -> получает путь к папке, где лежит этот файл (config.py)
#    os.path.abspath(...) -> превращает его в полный, абсолютный путь
basedir = os.path.abspath(os.path.dirname(__file__))

# 3. Теперь, когда 'basedir' определена, мы можем ее использовать внутри класса
class Config:
    """Класс конфигурации приложения."""
    
    # Секретный ключ для защиты сессий
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sluchainiy-nabor-simvolov-dlya-testa'
    
    # Строка подключения к базе данных
    # Мы используем 'basedir', чтобы построить правильный путь к файлу БД
    # и добавляем '?timeout=15', чтобы избежать ошибок блокировки
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'festival.db') + '?timeout=15'

    # Отключаем отслеживание модификаций, чтобы не было лишних предупреждений
    SQLALCHEMY_TRACK_MODIFICATIONS = False