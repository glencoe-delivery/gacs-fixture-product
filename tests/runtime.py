"""Consumer behaviour: the web client's calls, run against the provider, behave as the client expects."""

import sys

from harness import Report, call, server


def main():
    base, srv = server.start()
    r = Report("runtime")
    made = {}

    def create():
        status, body = call(base, "POST", "/v1/tenants/a/notes", "a-writer", {"text": "from the web client"})
        assert status == 201 and body["text"] == "from the web client", (status, body)
        made.update(body)

    def read():
        status, body = call(base, "GET", f"/v1/tenants/a/notes/{made['id']}", "a-reader")
        assert status == 200 and body["id"] == made["id"], (status, body)

    r.case("gacs.runtime", "POST /v1/tenants/{tenant_id}/notes", create)
    r.case("gacs.runtime", "GET /v1/tenants/{tenant_id}/notes/{note_id}", read)
    srv.shutdown()
    return r.write()


if __name__ == "__main__":
    sys.exit(main())
