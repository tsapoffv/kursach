FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@example.com
ENV DJANGO_SUPERUSER_PASSWORD=admin123

CMD sh -c "python manage.py migrate --noinput && \
    echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username=\"$DJANGO_SUPERUSER_USERNAME\").exists() or User.objects.create_superuser(\"$DJANGO_SUPERUSER_USERNAME\", \"$DJANGO_SUPERUSER_EMAIL\", \"$DJANGO_SUPERUSER_PASSWORD\")' | python manage.py shell && \
    python manage.py runserver 0.0.0.0:8000"