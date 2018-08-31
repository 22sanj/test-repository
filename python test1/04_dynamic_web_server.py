# coding:utf-8

import socket
import re
import sys

from multiprocessing import Process

# 设置静态文件根目录
HTML_ROOT_DIR = "./html"

WSGI_PYTHON_DIR = "./wsgipython"


class HTTPServer(object):
    """"""

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # print(1199)

    def start(self):
        # print("start")
        self.server_socket.listen(128)
        while True:
            # print("accept")
            client_socket, client_address = self.server_socket.accept()
            # print("accept1111")
            # print("[%s, %s]用户连接上了" % （client_address[]）)
            print("[%s]用户连接上了"%client_address[0])
            handle_client_process = Process(target=self.handle_client, args=(client_socket,))
            handle_client_process.start()
            client_socket.close()

    def start_response(self, status, headers):
        """
         status = "200 OK"
    headers = [
        ("Content-Type", "text/plain")
    ]
    star 
        """
        response_headers = "HTTP/1.1 " + status + "\r\n"
        for header in headers:
            response_headers += "%s: %s\r\n" % (header)

        self.response_headers = response_headers

    def handle_client(self, client_socket):
        """处理客户端请求"""
        # 获取客户端请求数据
        request_data = client_socket.recv(1024)
        print("request data:", request_data)
        request_lines = request_data.splitlines()
        for line in request_lines:
            print(line)

        # 解析请求报文
        # 'GET / HTTP/1.1'
        request_start_line = request_lines[0]
        # 提取用户请求的文件名
        print("*" * 10)
        print(request_start_line.decode("utf-8"))
        file_name = re.match(r"\w+ +(/[^ ]*) ", request_start_line.decode("utf-8")).group(1)
        method = re.match(r"(\w+) +/[^ ]* ", request_start_line.decode("utf-8")).group(1)

        # "/ctime.py"
        # "/sayhello.py"
        if file_name.endswith(".py"):
            try:
                m = __import__(file_name[1:-3])
                # print("2222")
            except Exception:
                self.response_headers = "HTTP/1.1 404 Not Found\r\n"
                response_body = "not found"
            else:
                env = {
                    # "PATH_INFO": file_name,
                    # "METHOD": method
                }
                response_body = m.application(env, self.start_response)

            response = self.response_headers + "\r\n" + response_body
            print("response:%s" % response)
            # print("11111")

        else:
            if "/" == file_name:
                # print("999999")
                file_name = "/index.html"

            #  打开文件，读取内容
            try:
                file = open(HTML_ROOT_DIR + file_name, "rb")
            except IOError:
                response_start_line = "HTTP/1.1 404 Not Found\r\n"
                response_headers = "Server: My server\r\n"
                response_body = "The file is not found!"
            else:
                file_data = file.read()
                file.close()

                # 构造响应数据
                response_start_line = "HTTP/1.1 200 OK\r\n"
                response_headers = "Server: My server\r\n"
                response_body = file_data.decode("utf-8")

            response = response_start_line + response_headers + "\r\n" + response_body
            print("response data1111:%s" % response)

        # 向客户端返回响应数据
        client_socket.send(bytes(response, "utf-8"))
        # client_socket.send(response.encode("utf-8"))

        # 关闭客户端连接
        client_socket.close()
        print("进程已关闭")

    def bind(self, port):
        self.server_socket.bind(("", port))


def main():
    sys.path.insert(1, WSGI_PYTHON_DIR)
    http_server = HTTPServer()
    http_server.bind(8000)
    http_server.start()


if __name__ == "__main__":
    main()
