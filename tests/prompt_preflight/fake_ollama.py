"""A stdlib stand-in for Ollama's /api/chat, used by the tests. No real model is ever needed."""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GOOD = {"verdict": "google", "confidence": 0.9, "google_query": "python reverse list"}


class FakeOllama:
    """mode: ok | bad_json | off_schema | slow | http_500. `reply` is the verdict dict for 'ok'."""

    def __init__(self, mode="ok", reply=None, delay=0.0):
        self.mode = mode
        self.reply = reply if reply is not None else dict(GOOD)
        self.delay = delay
        self.requests = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                outer.requests.append({"path": self.path, "body": json.loads(self.rfile.read(length) or b"{}")})
                if outer.mode == "slow":
                    time.sleep(outer.delay)
                if outer.mode == "http_500":
                    self.send_response(500)
                    self.end_headers()
                    return
                if outer.mode == "bad_json":
                    content = "this is not json"
                elif outer.mode == "off_schema":
                    content = json.dumps({"verdict": "shout", "confidence": 5})
                else:
                    content = json.dumps(outer.reply)
                payload = json.dumps({"message": {"role": "assistant", "content": content}}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                try:
                    self.wfile.write(payload)
                except OSError:
                    pass

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
