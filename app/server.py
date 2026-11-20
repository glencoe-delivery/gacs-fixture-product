"""The fixture product's API: a multi-tenant notes service. The tenant and scopes come from the bearer token."""

import itertools
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKENS = {  # token -> (tenant, scopes)
    "a-writer": ("a", {"notes:read", "notes:write"}),
    "a-reader": ("a", {"notes:read"}),
    "a-none": ("a", set()),
    "b-writer": ("b", {"notes:read", "notes:write"}),
}
NOTE = re.compile(r"^/v1/tenants/([^/]+)/notes/([^/]+)$")
NOTES = re.compile(r"^/v1/tenants/([^/]+)/notes$")


class App(BaseHTTPRequestHandler):
    store: dict = {}
    ids = itertools.count(1)

    def log_message(self, *args):
        pass

    def _send(self, status, body, kind="application/json"):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _problem(self, status, title):
        self._send(status, {"type": "about:blank", "title": title, "status": status}, "application/problem+json")

    def _caller(self, tenant, scope):
        """(ok) or sends the refusal: 401 no credential, 404 another tenant (never revealed), 403 missing scope."""
        auth = self.headers.get("Authorization", "")
        who = TOKENS.get(auth[7:]) if auth.startswith("Bearer ") else None
        if who is None:
            self._problem(401, "Unauthorized")
        elif who[0] != tenant:
            self._problem(404, "Not Found")
        elif scope not in who[1]:
            self._problem(403, "Forbidden")
        else:
            return True
        return False

    def do_GET(self):
        if self.path == "/v1/health":
            return self._send(200, {"status": "ok"})
        m = NOTE.match(self.path)
        if not m:
            return self._problem(404, "Not Found")
        tenant, note = m.groups()
        if self._caller(tenant, "notes:read"):
            found = self.store.get((tenant, note))
            self._send(200, found) if found else self._problem(404, "Not Found")

    def do_POST(self):
        m = NOTES.match(self.path)
        if not m:
            return self._problem(404, "Not Found")
        tenant = m.group(1)
        if not self._caller(tenant, "notes:write"):
            return
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"null")
        except ValueError:
            body = None
        if not isinstance(body, dict) or set(body) != {"text"} or not isinstance(body["text"], str) or not 1 <= len(body["text"]) <= 500:
            return self._problem(400, "Bad Request")
        note = {"id": f"n{next(self.ids)}", "tenant_id": tenant, "text": body["text"]}
        self.store[(tenant, note["id"])] = note
        self._send(201, note)


def start():
    """A running server on a free port, in a background thread. Returns (base_url, server)."""
    import threading
    srv = ThreadingHTTPServer(("127.0.0.1", 0), App)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}", srv
