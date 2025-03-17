import socket
import os
import json

HOST, PORT = "0.0.0.0", 3000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_file(path, content_type):
    try:
        with open(path, "rb") as f:
            content = f.read()
        return f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode() + content
    except FileNotFoundError:
        return read_error_page()

def read_error_page():
    path = os.path.join(BASE_DIR, "error.html")
    try:
        with open(path, "rb") as f:
            content = f.read()
        return f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n".encode() + content
    except FileNotFoundError:
        return b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Page Not Found"

def send_message(username, message):
    data = json.dumps({"username": username, "message": message})

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("socket_server", 5000))  # Змінено localhost на socket_server
        sock.sendall(data.encode())
        response = sock.recv(1024).decode("utf-8", errors="replace")
        return response

def handle_message_form(request):
    if "POST /message" in request:
        headers, body = request.split("\r\n\r\n", 1)
        params = dict(param.split("=") for param in body.split("&"))
        username = params.get("username", "")
        message = params.get("message", "")

        response = send_message(username, message)
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\n\r\n{response}".encode()
    return None

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"HTTP-сервер працює на {HOST}:{PORT}")

    while True:
        client, address = server.accept()
        with client:
            request = client.recv(1024).decode()
            if not request.strip():
                continue

            response = handle_message_form(request)

            if response is None:
                path = request.split(" ")[1]
                if path == "/":
                    path = "/index.html"

                file_path = os.path.join(BASE_DIR, path.lstrip("/"))

                if path.endswith(".html"):
                    response = read_file(file_path, "text/html")
                elif path.endswith(".css"):
                    response = read_file(file_path, "text/css")
                elif path.endswith(".png"):
                    response = read_file(file_path, "image/png")
                else:
                    response = read_error_page()

            if response:
                client.sendall(response)
