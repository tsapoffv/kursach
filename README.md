# Система управления расписанием

Учебная система для отображения и управления расписанием занятий в университете.

## Требования

- Python 3.13+
- PostgreSQL 15+
- Ubuntu/Linux (или Windows с WSL)

## Установка и запуск

### 1. Клонирование и настройка окружения

```bash
git clone <репозиторий>
cd kursach
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка PostgreSQL

```bash
# Создание пользователя и базы данных (от имени postgres)
sudo -u postgres psql

CREATE DATABASE schedule_db;
CREATE USER schedule_user WITH PASSWORD 'твой_пароль';
GRANT ALL PRIVILEGES ON DATABASE schedule_db TO schedule_user;
ALTER USER schedule_user WITH SUPERUSER;
\q
```

### 3. Настройка проекта

Отредактируй файл `schedule_project/settings.py`:
- `PASSWORD` в DATABASES — твой пароль от PostgreSQL

### 4. Запуск миграций

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Запуск сервера

```bash
python manage.py runserver
```

Открой в браузере: http://127.0.0.1:8000

## Функционал

- Просмотр списка учебных групп
- Расписание групп по неделям (А/Б)
- Поиск преподавателя с автодополнением
- Поиск аудитории с автодополнением
- Клик по преподавателю/аудитории -> переход к их расписанию

## Использование

1. **Главная страница** — выбор группы из списка
2. **Расписание группы** — занятия по дням недели
3. **Поиск преподавателя** — введите ФИО в поле слева
4. **Поиск аудитории** — введите номер аудитории

## Структура проекта

```
kursach/
├── schedule/              # Приложение расписания
│   ├── migrations/      # Миграции БД
│   ├── templates/     # HTML-шаблоны
│   ├── views.py      # Представления
│   ├── models.py    # Модели БД
│   └── urls.py      # URL-маршруты
├── schedule_project/    # Проект Django
│   ├── settings.py  # Настройки
│   └── urls.py     # Главные URL
├── venv/             # Виртуальное окружение
├── manage.py         # Точка входа
└── README.md        # Этот файл
```