from extensions import db
from sqlalchemy import CheckConstraint
from flask_login import UserMixin  # 1. Импортируем UserMixin для интеграции с Flask-Login

# 2. Добавляем UserMixin в объявление класса
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    nickname = db.Column(db.String(100), nullable=True, index=True)
    telegram_id = db.Column(db.String, nullable=True)
    role = db.Column(db.String, nullable=False)
    experience_category = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # 3. Добавляем поле для хранения уникального токена сессии
    session_token = db.Column(db.String(100), unique=True, nullable=True)

    participations = db.relationship('Participation', backref='user', cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("role IN ('participant', 'judge', 'admin')", name="check_role"),
        CheckConstraint("experience_category IN ('pro', 'junior') OR experience_category IS NULL", name="check_experience_category"),
    )