# Система расписаний

## Запуск (Docker)

```bash
docker-compose up --build
```

## Настройка суперпользователя

В `docker-compose.yml` изменить:
```yaml
environment:
  - DJANGO_SUPERUSER_USERNAME=admin
  - DJANGO_SUPERUSER_PASSWORD=ваш_пароль
  - DJANGO_SUPERUSER_EMAIL=admin@example.com
```

## Импорт расписания

1. Войти в админку: `/admin/schedule` и нажать кнопку справа "ИМПОРТ РАСПИСАНИЯ"
2. Загрузить `.docx` файл с расписанием
3. Нажать "Импорт из Word"

## Доступ

- Сайт: `http://localhost:8000`
- Админка: `http://localhost:8000/admin`
