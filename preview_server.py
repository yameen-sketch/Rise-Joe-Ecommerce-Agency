"""Local preview server that mimics the Hostinger .htaccess clean-URL rules.

    python3 preview_server.py        # then open http://localhost:8765/
"""
import http.server
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent / "website"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def _redirect(self, to):
        self.send_response(301)
        self.send_header("Location", to)
        self.end_headers()

    def do_GET(self):
        path, _, query = self.path.partition("?")
        q = ("?" + query) if query else ""
        disk = ROOT / path.lstrip("/")
        # /x/index.html -> /x/   and   /about.html -> /about
        if path.endswith("index.html"):
            return self._redirect(path[:-10] + q)
        if path.endswith(".html"):
            return self._redirect(path[:-5] + q)
        # /about/ -> /about
        if path != "/" and path.endswith("/") and not disk.is_dir():
            return self._redirect(path.rstrip("/") + q)
        # /about -> about.html
        if not disk.exists() and Path(str(disk) + ".html").is_file():
            self.path = path + ".html" + q
        elif not disk.exists():
            self.path = "/404.html"
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()


    def do_POST(self):
        # This lightweight server can't run PHP. Use the Docker preview for working forms.
        import json
        body = json.dumps({"ok": False, "message": "Forms need PHP. This simple preview can't send email: run the PHP preview (see DEPLOY.md) or test on the live site."}).encode()
        self.send_response(501)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    os.chdir(ROOT)
    print(f"Serving {ROOT} at http://localhost:{PORT}/")
    http.server.ThreadingHTTPServer(("", PORT), Handler).serve_forever()
