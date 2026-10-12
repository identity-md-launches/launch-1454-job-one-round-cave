# Anchor bridge

`anchor_bridge.py` is a compact offline glue piece between Line 1's block-pinned
snapshot and Line 4's validated ERC-20 transfer window. It emits a receipt only
when their exact closing block number **and** hash agree. That lets a worker
state that two supplied observations share an anchor without silently treating
nearby blocks as the same observation.

It accepts Line 1 Hash Snapshot v1 (`anchor`) and the earlier pinned-snapshot
shape (`block`), plus Line 4's schema-2 closing anchor. Inputs are explicit,
bounded JSON files; duplicate keys, malformed hashes, wrong-chain/unvalidated
windows, conflicting ranges and differing anchors fail closed. It uses Python's
standard library only, makes no network calls, writes no archive, executes no
payload, and has no wallet, key, signing or transaction path.

Try its full offline path from the repository root:

```sh
python3 -B shared/anchor-bridge/anchor_bridge.py demo
python3 -B shared/anchor-bridge/test_anchor_bridge.py
```

The demo prints an in-memory ZTO-labelled linkage at block 42 and the test suite
passed five checks: successful linkage, range conflict, hash mismatch, legacy
pinned shape, and duplicate-key CLI refusal with no stdout receipt. For real
files, pass a Hash Snapshot first and a transfer-window JSON second:

```sh
python3 -B shared/anchor-bridge/anchor_bridge.py link snapshot.json transfers.json
```

A receipt is integrity metadata about the supplied bytes, not proof of chain
finality, provider trust, event completeness, balances, or atomic collection.
