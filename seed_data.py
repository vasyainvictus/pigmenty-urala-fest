import random
import string
from datetime import datetime, date
from app import create_app
from extensions import db
from models import User, Festival, EventDay, NominationTemplate, TimeSlot, JudgeNomination, Criterion, Participation, Winner, Score

# Функция для генерации случайного 6-значного кода
def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Создаем экземпляр приложения, чтобы получить контекст
app = create_app()

with app.app_context():
    # --- 1. ОЧИСТКА ДАННЫХ ---
    print("Очистка старых данных...")
    db.session.query(Score).delete()
    db.session.query(Winner).delete()
    db.session.query(Participation).delete()
    db.session.query(JudgeNomination).delete()
    db.session.query(TimeSlot).delete()
    db.session.execute(db.text('DELETE FROM nomination_template_criteria'))
    db.session.query(Criterion).delete()
    db.session.query(NominationTemplate).delete()
    db.session.query(EventDay).delete()
    db.session.query(Festival).delete()
    db.session.query(User).delete()
    db.session.commit()
    print("Очистка завершена.")

    # --- 2. СОЗДАНИЕ ДАННЫХ ---
    print("Добавление тестовых данных...")
    
    try:
        # --- Пользователи ---
        admin = User(code='ADMIN1', role='admin', nickname='Главный Админ')
        db.session.add(admin)

        # 30 Судей
        judges = [User(code=generate_random_code(), role='judge', nickname=f'Судья {i}') for i in range(1, 31)]
        db.session.add_all(judges)

        # 20 Участников-юниоров
        junior_participants = [User(code=generate_random_code(), role='participant', nickname=f'Ю{i}', experience_category='junior') for i in range(1, 21)]
        db.session.add_all(junior_participants)
        
        # 20 Участников-профессионалов
        pro_participants = [User(code=generate_random_code(), role='participant', nickname=f'П{i}', experience_category='pro') for i in range(1, 21)]
        db.session.add_all(pro_participants)
        
        db.session.commit()
        print(f"Создано: 1 админ, {len(judges)} судей, {len(junior_participants)} юниоров и {len(pro_participants)} профи.")

        # --- Фестиваль и Дни ---
        festival = Festival(name='Пигменты Урала 2025', start_date=date(2025, 8, 15), end_date=date(2025, 8, 17))
        db.session.add(festival)
        db.session.commit()
        day1 = EventDay(festival_id=festival.id, date=date(2025, 8, 15), day_order=1)
        day2 = EventDay(festival_id=festival.id, date=date(2025, 8, 16), day_order=2)
        day3 = EventDay(festival_id=festival.id, date=date(2025, 8, 17), day_order=3)
        db.session.add_all([day1, day2, day3])
        db.session.commit()
        print(f"Создан фестиваль '{festival.name}' на 3 дня.")

        # --- Критерии с max_score=5 ---
        criteria_list = [
            Criterion(name='Техника', max_score=5, order=1),
            Criterion(name='Композиция', max_score=5, order=2),
            Criterion(name='Оригинальность', max_score=5, order=3),
            Criterion(name='Цвет', max_score=5, order=4),
            Criterion(name='Читаемость', max_score=5, order=5),
            Criterion(name='Анатомичность', max_score=5, order=6),
            Criterion(name='Масштаб', max_score=5, order=7),
            Criterion(name='Чистота', max_score=5, order=8),
            Criterion(name='Сложность', max_score=5, order=9),
            Criterion(name='Впечатление', max_score=5, order=10)
        ]
        db.session.add_all(criteria_list)
        db.session.commit()
        print(f"Создано {len(criteria_list)} критериев оценки (max_score=5).")

        # --- 20 Шаблонов номинаций ---
        nomination_names = [
            "Черно-белый реализм", "Цветной реализм", "Биомеханика", "Органика",
            "Японская татуировка", "Олд-скул", "Нью-скул", "Нео-традишнл",
            "Графика (Дотворк/Лайнворк)", "Орнаментальная татуировка", "Cover-up",
            "Портретная татуировка", "Миниатюрная татуировка", "Акварель",
            "Хоррор", "Леттеринг", "Сюрреализм", "Blackwork",
            "Лучшая татуировка дня", "Гран-при фестиваля"
        ]
        
        templates = []
        for name in nomination_names:
            template = NominationTemplate(
                name=name,
                participant_type=random.choice(['pro', 'both']), # Случайно pro или pro+junior
                description=f'Оценка работ в номинации «{name}»'
            )
            # Привязываем случайное количество (от 3 до 7) критериев к каждой номинации
            template.criteria = random.sample(criteria_list, k=random.randint(3, 7))
            templates.append(template)
            
        db.session.add_all(templates)
        db.session.commit()
        print(f"Создано {len(templates)} шаблонов номинаций.")

        # --- Создаем слоты-конкурсы в расписании (для примера) ---
        # Эта часть осталась для примера, вы можете расширить ее по аналогии
        all_templates = NominationTemplate.query.order_by(NominationTemplate.id).all()
        
        contest1 = TimeSlot(
            day_id=day1.id, start_time=datetime(2025, 8, 15, 10, 0), end_time=datetime(2025, 8, 15, 12, 0),
            slot_order=1, type='judging', nomination_template_id=all_templates[0].id, category='fresh', zone='A'
        )
        contest2 = TimeSlot(
            day_id=day1.id, start_time=datetime(2025, 8, 15, 13, 0), end_time=datetime(2025, 8, 15, 15, 0),
            slot_order=2, type='judging', nomination_template_id=all_templates[1].id, category='fresh', zone='Б'
        )
        db.session.add_all([contest1, contest2])
        db.session.commit()
        print("Созданы 2 примера слотов в расписании.")

        # --- Регистрируем участников и судей на конкурсы (для примера) ---
        all_participants = pro_participants + junior_participants
        
        # Регистрируем по 2 случайных участника на каждый конкурс
        for contest in [contest1, contest2]:
            participants_for_contest = random.sample(all_participants, k=2)
            for participant in participants_for_contest:
                db.session.add(Participation(user_id=participant.id, time_slot_id=contest.id, entry_number=1))
        
        # Назначаем по 3 случайных судьи на каждый конкурс
        for contest in [contest1, contest2]:
            judges_for_contest = random.sample(judges, k=3)
            for judge in judges_for_contest:
                db.session.add(JudgeNomination(judge_id=judge.id, time_slot_id=contest.id))

        db.session.commit()
        print("Примеры участников и судей зарегистрированы на конкурсы.")
        print("\nТестовые данные успешно добавлены!")

    except Exception as e:
        db.session.rollback()
        print(f"\nПроизошла ошибка при добавлении данных: {e}")