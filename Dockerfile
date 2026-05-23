FROM python:3.12-slim

# Настройки для стабильной работы Python в контейнере
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаем папку для проекта внутри виртуальной машины
WORKDIR /app

# Копируем список зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . /app/

# Собираем всю статику (HTML, CSS, JS) в одну папку для Whitenoise
RUN python manage.py collectstatic --noinput

# Открываем стандартный веб-порт
EXPOSE 8000

# Запускаем миграции, создаем админа (если его еще нет) и запускаем сервер
CMD ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser --noinput || true && gunicorn hospital_course.wsgi:application --bind 0.0.0.0:8000"]
