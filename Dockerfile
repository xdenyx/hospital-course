FROM python:3.12-slim

# Настройки для стабильной работы Python в контейнере
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаем папку для проекта внутри виртуальной машины
WORKDIR /app

# Копируем список зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код backend-приложения
COPY . /app/

# Открываем стандартный веб-порт
EXPOSE 8000

# Запускаем миграции и сам backend-сервер
CMD ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser --noinput || true && gunicorn hospital_course.wsgi:application --bind 0.0.0.0:8000"]
