# Handoff Catalog

Make a deterministic, offline-verifiable catalog of one or more fully verified
HANDOFF v1 ZIP files. A recipient can retain this small canonical JSON record
and later replay every inspection against the pinned archive hashes, without
extracting or executing a payload. Python 3.8+ and the standard library are
enough. From the workspace root, one command demonstrates it with the real
inherited handoff:

```sh
python3 -B line-2/tools/handoff-catalog/catalog.py demo
```

It cataloged `line-2/handoff.zip` in memory, replayed its pinned SHA-256, and
reported the verified archive's byte, file, and payload totals. The demo writes
nothing and neither extracts nor executes archive content.

To persist a new catalog for a recipient, choose a new path outside any source
directory and provide relative archive paths:

```sh
python3 -B line-2/tools/handoff-catalog/catalog.py make handoffs.json line-2/handoff.zip
python3 -B line-2/tools/handoff-catalog/catalog.py verify handoffs.json
```

`make` refuses to overwrite a file. Catalog JSON is canonical (sorted keys,
no whitespace beyond its final newline), has sorted distinct archive paths, and
pins each archive's SHA-256, byte count, payload file count, and payload-byte
total. `verify` first rejects malformed/noncanonical records, paths outside the
workspace, and symlinks; then it invokes the inherited bounded HANDOFF v1
inspector for every archive with its catalog digest. No network, environment
variables, keys, wallets, signatures, payments, uploads, extraction, or code
execution are used.

The catalog is an integrity receipt, not proof of who made an archive or that
its code is safe. Obtain its digest or the catalog itself through a trusted
channel, and inspect payloads separately.

```sh
python3 -B line-2/tools/handoff-catalog/test_catalog.py
```

When tried, all 9 tests passed, covering a real deterministic fixture,
replay, archive mutation, duplicate paths/JSON keys, canonical encoding,
outside paths, empty catalogs, and uppercase hashes.
