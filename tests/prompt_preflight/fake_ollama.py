"""A stdlib stand-in for Ollama's /api/chat, used by the tests. No real model is ever needed."""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GOOD = {"verdict": "google", "confidence": 0.9, "google_query": "python reverse list"}


class FakeOllama:
    """A local server that misbehaves on request.

    mode: ok | bad_json | off_schema | slow | http_500 | redirect | trickle | huge | deep | non_utf8 | content_not_string
    `reply` is the verdict dict for 'ok'. `delay` is in seconds: 'slow' waits that long before answering and
    'trickle' waits that long between the single bytes it sends. `redirect_to` is the Location for 'redirect'.
    """

    def __init__(self, mode="ok", reply=None, delay=0.0, redirect_to=""):
        self.mode = mode
        self.reply = reply if reply is not None else dict(GOOD)
        self.delay = delay
        self.redirect_to = redirect_to
        self.requests = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, status, body, content_type="application/json"):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _stream_headers(self, length):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(length))
                self.end_headers()

            def do_GET(self):
                outer.requests.append({"path": self.path, "body": None, "method": "GET"})
                self._send(404, b"")

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                outer.requests.append({"path": self.path, "body": json.loads(self.rfile.read(length) or b"{}")})
                try:
                    self._answer()
                except OSError:
                    pass  # the client gave up first: a timeout, the size cap, or a refused redirect

            def _answer(self):
                mode = outer.mode
                if mode == "slow":
                    time.sleep(outer.delay)
                if mode == "http_500":
                    return self._send(500, b"")
                if mode == "redirect":
                    self.send_response(302)
                    self.send_header("Location", outer.redirect_to)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if mode == "trickle":
                    self._stream_headers(100000)
                    for _ in range(60):
                        self.wfile.write(b" ")
                        self.wfile.flush()
                        time.sleep(outer.delay)
                    return
                if mode == "huge":
                    self._stream_headers(5000000)
                    for _ in range(5000):
                        self.wfile.write(b"x" * 1000)
                    return
                if mode == "deep":
                    return self._send(200, b"[" * 50000)
                if mode == "non_utf8":
                    return self._send(200, b"\xff\xfe\xfa")
                if mode == "bad_json":
                    content = "this is not json"
                elif mode == "off_schema":
                    content = json.dumps({"verdict": "shout", "confidence": 5})
                elif mode == "content_not_string":
                    content = 5
                else:
                    content = json.dumps(outer.reply)
                self._send(200, json.dumps({"message": {"role": "assistant", "content": content}}).encode())

        # Threading server: a sleeping 'slow' handler must not block shutdown. Fast poll: the
        # default 0.5 s shutdown poll would add half a second to every test.
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.host = "127.0.0.1:%d" % self._server.server_port
        self._thread = threading.Thread(
            target=lambda: self._server.serve_forever(poll_interval=0.01), daemon=True
        )

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._server.shutdown()
        self._server.server_close()
