# kursach

# Быстрый запуск (тестовый)

Требования
Python 3.13+
PostgreSQL


# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Выполнить скипт create_db.sql от имени psql

# Настройки БД в schedule_project/settings.py
PASSWORD = 'my_secret_pw'

# Генерация таблиц в бд
python manage.py migrate

# Делаем мокап бд
python manage.py populate_db

# Запуск
python manage.py runserver
