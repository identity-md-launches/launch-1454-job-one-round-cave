# Shared pieces

[`evidence-handoff/`](evidence-handoff/README.md) (gathering 01) shares Line 2's deterministic
handoff utility and joins the public JSON outputs from Lines 1, 3 and 4 into one
offline-verifiable archive. It has no network or third-party dependencies.

```sh
python3 -B shared/evidence-handoff/bundle.py demo
```

[`tx-preflight/`](tx-preflight/README.md) (gathering 02) joins Line 3's offline decoder with Line 1's
read-only RPC validators. It checks an unsigned EIP-1559 transaction against
live state pinned to one block: chain, fees, nonce, ETH for gas, and ERC-20
amount, balance and recipient. Every read is kept as a Line 1 snapshot, so the
same evidence replays offline.

```sh
python3 -B shared/tx-preflight/preflight.py demo
```

[`evidence-review/`](evidence-review/README.md) (gathering 03) copies the newer
line validators into a portable kit. It packages pinned ZTO supply, validated
transfer windows, recomputed provider comparisons and original unsigned RLP
with ERC-20 intent. Inspection verifies archive integrity and rebuilds evidence
summaries. Live capture supports the supplied relay and links observations with
matching closing block hashes.

```sh
python3 -B shared/evidence-review/review.py demo
```

Use Evidence review when raw logs, block anchors or original RLP must be
revalidated; the first Evidence handoff checks simpler producer shapes.

The original line folders are unchanged. These are reusable worker tools, not
record viewers.

[`handoff-revision/`](handoff-revision/README.md) (gathering 04) joins Line 2's
verified archive and source comparisons with Line 3's complete unsigned-envelope
comparison. A worker sees file changes and exact transaction changes together,
and can check that the revised bundle still matches its public source directory.
The folder is portable and uses only the Python standard library.

```sh
python3 -B shared/handoff-revision/revision.py demo
```

[`anchor-bridge/`](anchor-bridge/README.md) (gathering 05) is a small offline
join for Line 1's block-pinned snapshot and Line 4's validated transfer window.
It emits a receipt only when both supplied observations have the exact same
closing block hash and height.

```sh
python3 -B shared/anchor-bridge/anchor_bridge.py demo
```

[`anchor-bridge/`](anchor-bridge/README.md) (gathering 05) is a small offline
join for Line 1's block-pinned snapshot and Line 4's validated transfer window.
It emits a receipt only when both supplied observations have the exact same
closing block hash and height.

```sh
python3 -B shared/anchor-bridge/anchor_bridge.py demo
```
