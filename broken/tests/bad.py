"""Negative control: each mode writes evidence GACS must refuse, while exiting 0 (success proves nothing).

  skipped     conformance with one case skipped
  incomplete  security that passes, but omits every cross_tenant case
  silent      runtime that exits 0 and writes no report
  malformed   static whose report is not XML"""

import os
import sys
from pathlib import Path

mode = sys.argv[1]
OPS = ["GET /v1/health", "POST /v1/tenants/{tenant_id}/notes", "GET /v1/tenants/{tenant_id}/notes/{note_id}"]
SECURED = OPS[1:]


def report(cases):
    rows = ['<testsuite name="bad">']
    for cls, name, extra in cases:
        rows.append(f'<testcase classname="{cls}" name="{name}">{extra}</testcase>')
    Path(os.environ["GACS_REPORT"]).write_text("\n".join(rows + ["</testsuite>"]))


if mode == "skipped":
    report([("gacs.conformance", op, "<skipped/>" if i == 0 else "") for i, op in enumerate(OPS)])
elif mode == "incomplete":
    report([("gacs.security", f"{op} {case}", "") for op in SECURED for case in ("unauthenticated", "unauthorized")])
elif mode == "malformed":
    Path(os.environ["GACS_REPORT"]).write_text("<testsuite><testcase classname='x' name='y'>")
sys.exit(0)
