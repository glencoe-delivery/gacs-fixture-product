"""Shared test plumbing for the fixture product: HTTP calls, and a JUnit report written to $GACS_REPORT."""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import server  # noqa: E402

CONTRACT = json.loads((Path(__file__).resolve().parents[1] / "api" / "openapi.json").read_text())


def call(base, method, path, token=None, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


class Report:
    def __init__(self, suite):
        self.suite, self.cases = suite, []

    def case(self, classname, name, fn):
        try:
            fn()
            self.cases.append((classname, name, None))
        except AssertionError as exc:
            self.cases.append((classname, name, str(exc) or "assertion failed"))

    def write(self):
        failures = sum(1 for c in self.cases if c[2])
        rows = [f'<testsuite name={quoteattr(self.suite)} tests="{len(self.cases)}" failures="{failures}">']
        for cls, name, err in self.cases:
            inner = f"<failure message={quoteattr(err)}/>" if err else ""
            rows.append(f"  <testcase classname={quoteattr(cls)} name={quoteattr(name)}>{inner}</testcase>")
        rows.append("</testsuite>")
        Path(os.environ["GACS_REPORT"]).write_text("\n".join(rows) + "\n")
        print(f"{self.suite}: {len(self.cases) - failures}/{len(self.cases)} passed")
        return 1 if failures else 0
