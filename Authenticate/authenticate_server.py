import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer


class AuthenticateServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.start()

    def run(self):
        handler = TestServer

        with HTTPServer(('', 80), handler) as httpd:
            httpd.serve_forever()


class TestServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        print('#### call do_GET()')
        super().do_GET()
