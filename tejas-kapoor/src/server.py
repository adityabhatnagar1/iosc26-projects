"""Local web UI for the phishing detector. Standard library only.

    python server.py            # http://127.0.0.1:8000
    python server.py 9000       # custom port
Binds to localhost only; nothing is sent anywhere.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from phishing_detector import EMAILS, THRESHOLD, analyze, evaluate, parse_raw

INDEX = Path(__file__).parent / "web" / "index.html"
MAX_BODY = 200_000


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload, ctype="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX.read_bytes(), "text/html")
        elif self.path == "/api/demo":
            rows, counts = evaluate(EMAILS)
            self._send(200, {"threshold": THRESHOLD, "rows": rows, "counts": counts})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/analyze":
            return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > MAX_BODY:
                return self._send(413, {"error": "email too large"})
            raw = json.loads(self.rfile.read(n))["raw"]
            score, verdict, hits = analyze(parse_raw(raw))
            self._send(200, {"score": score, "verdict": verdict, "threshold": THRESHOLD,
                             "indicators": [{"points": p, "text": m} for p, m in hits]})
        except Exception as exc:  # malformed input
            self._send(400, {"error": f"bad request: {exc}"})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Open http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
