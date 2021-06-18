import socket
from config import *
import os


class Response:
    def __init__(
            self,
            protocol: str = "HTTP/1.1",
            code: int = 200,
            status: str = "OK",
            headers: dict = None,
            body: str = ""
    ):
        self.protocol = protocol
        self.code = code
        self.status = status
        self.headers = headers
        if self.headers is None:
            self.headers = dict()
        self.body = body

    def concatenating(self) -> str:
        ans = list()
        ans.append(f'{self.protocol} {self.code} {self.status}')
        ans.append(SEPARATOR.join(map(lambda k, v: f'{k}: {v}', self.headers.keys(), self.headers.values())))
        ans.append(SEPARATOR)
        ans.append(self.body)
        return SEPARATOR.join(ans)


class Request:
    def __init__(
            self,
            method: str = "GET",
            url: str = "/",
            protocol: str = "HTTP/1.1",
            headers: dict = None,
            body: str = ""
    ):
        self.headers = headers
        if self.headers is None:
            self.headers = dict()
        self.method = method
        self.url = url
        self.protocol = protocol
        self.body = body

    @staticmethod
    def parse(request: str):
        ans = request.split(SEPARATOR)
        method, url, protocol = ans.pop(0).split()
        body_sep = ans.index("")
        headers = dict()
        for row in ans[:body_sep]:
            k, v = row.split(": ", 1)
            headers.update({k: v})
        body = SEPARATOR.join(ans[body_sep + 1:])
        return Request(method, url, protocol, headers, body)


def read_file(path: str) -> str:
    response = ""
    if os.path.isfile(path):
        file = open(path, 'r')
        for line in file:
            response += line + '\n'
    return response


def start_web_server():
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()
        data = conn.recv(MAX_REQ_SIZE)
        msg = data.decode(CHARSET)
        req = Request.parse(msg)

        code = 200
        status = 'OK'
        body = read_file(WORK_DIRECTORY + req.url.replace('/', '\\'))
        if body == "":
            code = 404
            status = 'NOT_FOUND'
        response = Response(
            code=code,
            status=status,
            headers={"Content-type": f"text/html;charset={CHARSET}"},
            body=body
        )
        conn.send(response.concatenating().encode(CHARSET))
        conn.close()


if __name__ == '__main__':
    start_web_server()
