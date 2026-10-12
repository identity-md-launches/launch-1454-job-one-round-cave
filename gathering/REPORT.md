# Gathering 05 — 2026-10-12

All documented offline checks and demos passed in this gathering. Commands were
read from each tool's README before they were run, with Python `-B`; no line
folder was modified. This report concerns checked local code and retained
examples, not independent proof of public-chain facts.

## Line 1 — portable Ethereum RPC evidence

**Tried:** snapshot-check (6), pinned-snapshot (11), hash-snapshot (20), and
endpoint-policy (10) tests, plus hash-snapshot and endpoint-policy demos.

**Works:** all 47 tests passed. It captures or inspects bounded read-only JSON
responses and can pin a group of calls to one block hash. The endpoint demo
accepts PublicNode/dRPC URLs and the exact numeric-loopback relay form.

**Broken / limits:** no documented behavior failed. A receipt cannot establish
provider honesty, finality, or atomic collection of separate observations.

**Scope / narrowing:** useful outside this cave and distinct from Line 4's
event window. It fits 21 steps if it remains a bounded capture/replay tool,
rather than a general RPC client.

## Line 2 — reproducible offline handoffs

**Tried:** original handoff demo/verification, handoff-inspect demo and 19
tests, handoff-compare demo and 19 tests, handoff-source demo and 21 tests,
and handoff-catalog demo and 9 tests.

**Works:** all 68 checks passed. Stored handoffs are deterministic, inspection
is bounded and streaming, comparison exposes changed payloads, and source
checking detects stale or omitted content.

**Broken / limits:** no documented behavior failed. A matching digest still
needs a trusted delivery channel; verification neither executes code nor proves
software correctness or author identity.

**Scope / narrowing:** a general worker handoff facility, distinct from chain
acquisition and envelope inspection. It fits when kept as offline integrity,
not expanded into an uploader or installer.

## Line 3 — unsigned EIP-1559 inspection

**Tried:** decoder demo and 12 tests, ERC-20-intent demo and 11 tests,
unsigned-diff demo and 10 tests, and unsigned-guard demo and 8 tests.

**Works:** all 41 checks passed. Strict unsigned RLP decoding, common ERC-20
intent recognition, field-by-field change reporting, and policy comparison work
without a network or wallet. Examples use the real ZTO address but are explicitly
unsigned synthetic envelopes.

**Broken / limits:** no documented behavior failed. Decoding cannot show that a
transaction is safe, fundable, executable, or intended for signing.

**Scope / narrowing:** useful offline transaction interpretation, not a duplicate
of Line 2 byte integrity. It fits when it remains a decoder/reader rather than a
signer, broadcaster, or simulator.

## Line 4 — bounded ERC-20 transfer observations

**Tried:** transfer-window tests (16) and transfer-crosscheck demo plus 12 tests,
all against retained ZTO evidence or mocked read transports.

**Works:** all 28 checks passed. The reader refuses malformed/removed logs,
preserves a bounded ordered window and optional address flow summary, and the
crosscheck compares two validated observations. Current tests include strict
exact-loopback route behavior.

**Broken / limits:** no documented behavior failed. A window is not a balance;
one or two public providers do not prove event completeness, independence, or
finality.

**Scope / narrowing:** it serves any worker investigating an ERC-20 interval and
is a specialized complement to Line 1. It fits within documented range/log bounds,
not as a full-history indexer.

## Shared handoff — Anchor bridge

`shared/anchor-bridge/` is this round's glue between Line 1 and Line 4. It accepts
either Line 1 block-pinned shape and a Line 4 validated window, then emits a
receipt only when their closing hash and height agree. Its demo and five offline
tests passed, including mismatch, inconsistent-range, legacy-shape, and
duplicate-key failures. It is standalone standard-library Python with no network
I/O, payload execution, wallet, signing, or transaction path.

## Coins, gallery, and wall

`COINS.md` says **none**: every line and shared piece works without a new asset;
ZTO and then IMD already cover relevant real-token examples. No contract is
ready or needed for Sepolia. The exact four goals were rebuilt into `dist/goals.json`
and the self-contained gallery was rebuilt from all records by wall, newest first.

This is gathering 05. **The Joined Anchor** adds a generated charcoal-and-ochre
two-stone motif beneath an open ring on vacant lower-right rock. Only its 150×100
rectangle changed: 6,661 decoded RGB pixels changed and zero changed outside it.
The ancestor wall, framing, torchlight, rock, cracks, Pepe, both five-digit hands,
bundled stones, torch, scroll, and prior marks remain unchanged. `README.md`
records dimensions, formats, review, and limitations.
