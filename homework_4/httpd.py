from datetime import datetime
import socket
import logging
from urllib.parse import unquote
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

LOGGER = logging.getLogger(__name__)


def my_server():
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("localhost", 80))
        s.listen(5)
        print(f"Установлено соединение с {s.getsockname()}")
        print(f"Сервер {s}")
        while True:
            conn, addr = s.accept()
            print(f"con = {conn}")
            print(f"Соединение от {addr}")
            data = conn.recv(2048)
            if data:
                message = data.decode("utf-8")
                print(f"Получено сообщение: \n {message}")
                send_data = request_analyzer(message, s)
                bts = conn.send(str(send_data).encode("utf-8"))
            else:
                print("Нет сообщения от клиента")
                break
            print("Закрываю соединение")
            conn.close()


def request_analyzer(client_message, server):
    status_code = ""
    body = ""
    content_type = ""
    content_len = ""
    if len(client_message) == 1:
        status_code = "404 Not Found"
    else:
        message_list = client_message.split("\r\n")
        print(message_list)
        request_info = message_list[0].split()
        req_method = request_info[0]
        request_source = request_info[1]
        if req_method not in ["GET", "HEAD"]:
            status_code = "405 Method Not Allowed"
        else:
            if req_method == "GET":
                body, status_code, content_len = handle_get_source_request(
                    request_source
                )
            elif req_method == "HEAD":
                body, status_code, content_len = handle_head_request(request_source)
        content_type = handle_content_type(request_source)
    status_line = f"HTTP/1.1 {status_code}"
    headers = "\r\n".join(
        [
            status_line,
            f"Content-Type: {content_type}",
            "Connection: keep-alive",
            f'Date: {datetime.now().strftime("%m %d %Y, %H:%M:%S")}',
            f"Server: {server}",
            f"Content-Length: {content_len}",
        ]
    )

    body = str(body)
    print("Ответ клиенту")
    send_data = "\r\n\r\n".join([headers, body])

    return send_data


def handle_get_source_request(request_source):
    status_code = "200 OK"
    body = ""
    content_len = ""
    request_source = unquote(request_source)
    request_source = request_source.split("?")[0]
    try:
        try:
            if "/etc/passwd" in request_source:
                status_code = "403 Forbidden"
            if request_source.lstrip("/").endswith(
                (".gif", ".jpeg", ".jpg", ".png", ".swf")
            ):
                body, content_len = open_file_handler(
                    request_source.lstrip("/"), is_image=True
                )
            else:
                body, content_len = open_file_handler(request_source.lstrip("/"))
        except IsADirectoryError:
            body, content_len = open_file_handler(
                request_source.lstrip("/") + "index.html"
            )
    except FileNotFoundError:
        body = ""
        status_code = "404 Not Found"
    except NotADirectoryError:
        body = ""
        status_code = "404 Not Found"
    return body, status_code, content_len


def open_file_handler(request_source, is_image=False):
    if is_image:
        with open(request_source, "rb") as f:
            body = f.read()
            content_len = len(body)
    else:
        with open(request_source, "r", encoding="utf-8", errors="ignore") as f:
            body = f.read()
            content_len = len(body.encode("utf-8"))
    return body, content_len


def handle_head_request(request_source):
    body, status_code, content_len = handle_get_source_request(request_source)
    return "", status_code, content_len


def handle_content_type(request_source):
    if request_source.endswith(".html"):
        return "text/html"
    elif request_source.endswith(".css"):
        return "text/css"
    elif request_source.endswith(".js"):
        return "text/javascript"
    elif request_source.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    elif request_source.endswith(".png"):
        return "image/png"
    elif request_source.endswith(".gif"):
        return "image/gif"
    elif request_source.endswith(".swf"):
        return "application/x-shockwave-flash"


if __name__ == "__main__":
    my_server()
