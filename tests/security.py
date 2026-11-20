"""U10 for every secured operation: no credential (401), a credential without the scope (403), and another
tenant's credential (404, revealing nothing). The cases are named as GACS requires."""

import sys

from harness import Report, call, server


def main():
    base, srv = server.start()
    _, note = call(base, "POST", "/v1/tenants/a/notes", "a-writer", {"text": "secret"})
    ops = {
        "POST /v1/tenants/{tenant_id}/notes": ("POST", "/v1/tenants/a/notes", {"text": "x"}),
        "GET /v1/tenants/{tenant_id}/notes/{note_id}": ("GET", f"/v1/tenants/a/notes/{note['id']}", None),
    }
    r = Report("security")
    for name, (method, path, body) in ops.items():
        def expect(token, want, method=method, path=path, body=body):
            def check():
                status, problem = call(base, method, path, token, body)
                assert status == want and problem.get("status") == want, (status, problem)
            return check
        r.case("gacs.security", f"{name} unauthenticated", expect(None, 401))
        r.case("gacs.security", f"{name} unauthorized", expect("a-none", 403))
        r.case("gacs.security", f"{name} cross_tenant", expect("b-writer", 404))
    srv.shutdown()
    return r.write()


if __name__ == "__main__":
    sys.exit(main())
