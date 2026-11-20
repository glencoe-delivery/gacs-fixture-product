"""The consumer's static check: every call in the web client names an operation of the contract it was built
against. (A TypeScript product would run its typecheck against the generated client here.)"""

import json
import re
import sys
from pathlib import Path

from harness import Report

ROOT = Path(__file__).resolve().parents[1]


def main():
    contract = json.loads((ROOT / "web" / "contracts" / "notes.json").read_text())
    ops = {f"{m.upper()} {p}" for p, item in contract["paths"].items() for m in item}
    r = Report("static")
    for f in sorted((ROOT / "web" / "src").rglob("*.ts")):
        for m in re.finditer(r'client\.(GET|POST|PUT|PATCH|DELETE)\("([^"]+)"', f.read_text()):
            op = f"{m.group(1)} {m.group(2)}"

            def check(op=op):
                assert op in ops, f"{op} is not in the contract the client was built against"
            r.case("static.client", op, check)
    return r.write()


if __name__ == "__main__":
    sys.exit(main())
