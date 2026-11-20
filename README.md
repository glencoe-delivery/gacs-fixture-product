# GACS fixture product

Synthetic test data for Glencoe's API contract evidence checks. It is not a product and holds no
credentials: the bearer tokens in `app/server.py` are made-up test strings for a local, in-memory server.

- The root is a positive control: a tiny multi-tenant notes API and a web client whose tests meet every
  required case, so its evidence must be **verified**.
- `broken/` is a negative control: every command exits 0, but its evidence is skipped, incomplete, missing
  or malformed, so it must be **refused** for each reason.

The checks run elsewhere and only read this repository, at an exact commit. Nothing runs here.
