"""Provider conformance: each operation answers as its contract says (status, media type and required fields)."""

import sys

from harness import CONTRACT, Report, call, server


def required(ref):
    return set(CONTRACT["components"]["schemas"][ref.rsplit("/", 1)[1]]["required"])


def main():
    base, srv = server.start()
    r = Report("conformance")

    def health():
        status, body = call(base, "GET", "/v1/health")
        assert status == 200 and required("#/components/schemas/Health") <= set(body), (status, body)

    def create():
        status, body = call(base, "POST", "/v1/tenants/a/notes", "a-writer", {"text": "hello"})
        assert status == 201 and required("#/components/schemas/Note") <= set(body), (status, body)
        status, body = call(base, "POST", "/v1/tenants/a/notes", "a-writer", {"text": ""})
        assert status == 400 and required("#/components/schemas/Problem") <= set(body), (status, body)

    def read():
        _, made = call(base, "POST", "/v1/tenants/a/notes", "a-writer", {"text": "x"})
        status, body = call(base, "GET", f"/v1/tenants/a/notes/{made['id']}", "a-reader")
        assert status == 200 and body == made, (status, body)
        status, _ = call(base, "GET", "/v1/tenants/a/notes/missing", "a-reader")
        assert status == 404, status

    r.case("gacs.conformance", "GET /v1/health", health)
    r.case("gacs.conformance", "POST /v1/tenants/{tenant_id}/notes", create)
    r.case("gacs.conformance", "GET /v1/tenants/{tenant_id}/notes/{note_id}", read)
    srv.shutdown()
    return r.write()


if __name__ == "__main__":
    sys.exit(main())
