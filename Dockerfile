# Використовуємо офіційний образ Python 3.11
FROM python:3.11

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо всі файли проєкту в контейнер
COPY . .

# Встановлюємо pymongo
RUN pip install pymongo

# Додаємо команду запуску для веб-сервера
CMD ["python", "main.py"]
