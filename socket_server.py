import socket
import json
import os
from datetime import datetime, UTC
from pymongo import MongoClient

# Підключення до MongoDB через змінну середовища
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/")
try:
    client = MongoClient(MONGO_URL)
    db = client["form_db"]
    collection = db["messages"]
    print("Підключено до MongoDB")
except Exception as e:
    print(f"Помилка підключення до MongoDB: {e}")
    exit(1)

# Параметри сервера
HOST, PORT = "0.0.0.0", 5000

# Створюємо TCP-сокет
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Socket-сервер працює на {HOST}:{PORT}")

    while True:
        client_socket, address = server.accept()
        with client_socket:
            try:
                data = client_socket.recv(1024).decode("utf-8")
                print(f"Отримано запит: {data}")

                if not data.strip():
                    print("Отримано порожній запит")
                    error_response = json.dumps({"status": "ERROR", "message": "Порожній запит"}, ensure_ascii=False)
                    client_socket.sendall(error_response.encode("utf-8"))
                    continue

                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    print("Невірний формат JSON")
                    error_response = json.dumps({"status": "ERROR", "message": "Невірний формат JSON"}, ensure_ascii=False)
                    client_socket.sendall(error_response.encode("utf-8"))
                    continue

                if not isinstance(message, dict) or "username" not in message or "message" not in message:
                    print("Некоректний запит: немає обов’язкових полів")
                    error_response = json.dumps({"status": "ERROR", "message": "Очікується JSON з 'username' та 'message'"}, ensure_ascii=False)
                    client_socket.sendall(error_response.encode("utf-8"))
                    continue

                username = str(message["username"]).strip()
                text = str(message["message"]).strip()

                if not username or not text:
                    print("Некоректний запит: username або message порожні")
                    error_response = json.dumps({"status": "ERROR", "message": "Поле 'username' та 'message' не можуть бути порожні"}, ensure_ascii=False)
                    client_socket.sendall(error_response.encode("utf-8"))
                    continue

                new_message = {
                    "date": datetime.utcnow().isoformat(),
                    "username": username,
                    "message": text
                    
                }

                try:
                    collection.insert_one(new_message)
                    print(f"Збережено: {new_message}")
                except Exception as e:
                    print(f"Помилка збереження в MongoDB: {e}")
                    client_socket.sendall(json.dumps({"status": "ERROR", "message": "Помилка БД"}).encode("utf-8"))
                    continue

                response = json.dumps({"status": "OK", "message": "Повідомлення отримано"}, ensure_ascii=False)
                client_socket.sendall(response.encode("utf-8"))
                print("Відповідь надіслано")

            except Exception as e:
                print(f"Загальна помилка сервера: {e}")
                error_response = json.dumps({"status": "ERROR", "message": "Помилка сервера"}, ensure_ascii=False)
                client_socket.sendall(error_response.encode("utf-8"))
