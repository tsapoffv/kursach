# Команды Django

## Запуск сервера

```bash
# Запуск локального сервера
python manage.py runserver

# Запуск на конкретном порту
python manage.py runserver 8000

# Запуск с указанием IP и порту
python manage.py runserver 0.0.0.0:8000
```

## Миграции БД

```bash
# Создание миграций для изменений в моделях
python manage.py makemigrations

# Создание миграций для конкретного приложения
python manage.py makemigrations schedule

# Применение всех миграций
python manage.py migrate

# Применение миграций для конкретного приложения
python manage.py migrate schedule

# Показать список миграций и их статус
python manage.py showmigrations

# Показать SQL для миграции (не выполняет её)
python manage.py sqlmigrate schedule 0001_initial

# Пометить миграцию как выполненную (без выполнения)
python manage.py migrate schedule 0001_initial --fake
```

## Суперпользователь

```bash
# Создание суперпользователя
python manage.py createsuperuser

# Изменение пароля пользователя
python manage.py changepassword <username>
```

## Проверка и отладка

```bash
# Проверка проекта на ошибки
python manage.py check

# Открыть REPL Django
python manage.py shell

# Открыть SQL-оболочку БД
python manage.py dbshell

# Запуск тестов
python manage.py test
```

## Статические файлы

```bash
# Сбор статических файлов в STATIC_ROOT
python manage.py collectstatic
```

## Создание проектов/приложений

```bash
# Создание нового проекта
python manage.py startproject <project_name>

# Создание нового приложения
python manage.py startapp <app_name>
```

## Данные

```bash
# Экспорт данных в JSON
python manage.py dumpdata schedule > schedule.json

# Импорт данных из JSON
python manage.py loaddata schedule.json

# Очистка БД (удаление всех данных, структура остаётся)
python manage.py flush
```

## Команды приложения schedule

```bash
# Заполнение БД тестовыми данными
python manage.py populate_db
```