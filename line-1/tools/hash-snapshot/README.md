# Hash snapshot

Capture several read-only Ethereum contract responses against **one block hash**, then inspect the portable JSON entirely offline. This extends Line 1's numbered-block ZTO snapshot with EIP-1898 `eth_call` references: every call includes the identical `blockHash` and `requireCanonical: true`. It supports 1–16 caller-described `to`/`data` calls, and defaults to real ZTO and IMD supplies and decimals. Python standard library only; keep the sibling `rpc-snapshot/` folder for its reviewed address, request, response and endpoint validators.

One command from the repository root shows the retained real observation working **without a network**:

```sh
python3 -B line-1/tools/hash-snapshot/hash_snapshot.py demo
```

It prints the block identity, original return bytes, call destinations and selectors, and exact decimal integer strings for recognized ZTO/IMD ABI results. This is useful to a worker collecting several state observations for an offline report or handoff. The inspector itself never makes network requests.

## What happened when tried

The supplied worker relay `http://127.0.0.1:35547/rpc/1` completed seven read-only requests at **2026-10-12T18:03:27Z**: chain ID, finalized block anchor, four hash-pinned calls, and the anchor at its explicit number again. Block **26177975**, hash **0x29d210293990d54ba91744fafc312c07cbc2058b6224980506bc5866a04e4073**, was unchanged. ZTO (`0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`) returned **1000000000000000000000000000** supply base units; IMD (`0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7`) returned **4176456975914000000000000**. Both returned **18** decimals. The actual call requests and complete JSON-RPC call envelopes are retained in `example-mainnet.json`; these are dated provider observations, not synthetic examples or current balances.

Twenty new offline tests passed. They cover all calls using one hash, explicit-number capture, early wrong-chain/block rejection, observed reorgs and changed timestamps/parents, malformed responses, hash-reference tampering, duplicate/non-finite JSON, ABI and size bounds, unsafe requests rejected before networking, raw generic responses, redirects, environment-proxy avoidance, offline CLI errors and failure without partial output. All 27 inherited Line 1 tests also passed. Local checks are observations, not independent certification.

```sh
python3 -B line-1/tools/hash-snapshot/test_hash_snapshot.py
```

## Fresh capture and offline replay

The relay URL works only on this worker machine. Another worker must use its own supplied relay port or a credential-free public HTTPS provider that supports EIP-1898:

```sh
python3 -B line-1/tools/hash-snapshot/hash_snapshot.py capture --rpc http://127.0.0.1:35547/rpc/1
```

JSON goes to stdout only after the entire capture validates. Save it inside your workspace and inspect it later:

```sh
python3 -B line-1/tools/hash-snapshot/hash_snapshot.py inspect < line-1/tools/hash-snapshot/example-mainnet.json
```

`--block` accepts `finalized` (default), `safe`, `latest`, `earliest`, or a canonical lowercase hexadecimal number. `pending` is rejected. To provide a different bounded call plan, pass `--calls-stdin` and a JSON list of objects with exactly `label`, `to` and `data`. Labels are unique ASCII names of 1–64 characters. For example, this reads the real ZTO supply:

```sh
python3 -B line-1/tools/hash-snapshot/hash_snapshot.py capture --rpc http://127.0.0.1:35547/rpc/1 --calls-stdin <<'JSON'
[{"label":"ZTO-supply","to":"0xd782bdea4ef02a0bd391eb9089470c8080f0a68e","data":"0x18160ddd"}]
JSON
```

No sender, value, gas, wallet or signing fields are accepted. `eth_call` executes only inside the provider's simulation and never submits a transaction. Only `eth_chainId`, `eth_getBlockByNumber` and hash-referenced `eth_call` are sent. Each request has a 20-second timeout, an explicit User-Agent and a 4 MiB response limit. Call data is bounded to 4096 bytes, return data to 64 KiB, and serialized snapshots/stdin to 1 MiB. Redirects are refused and proxy discovery from environment variables is disabled. Unsupported EIP-1898, noncanonical blocks, RPC errors or inconsistent anchors produce exit 1, a generic error on stderr, and no snapshot. There is **no fallback to a block-number call**. Inspect/demo success exits 0; malformed evidence exits 1.

## Evidence limits

The snapshot stores compact block identity fields (`number`, `hash`, `parentHash`, `timestamp`), not complete block responses. It preserves complete JSON-RPC call result envelopes and the chain-ID response. There is no receipt, state proof, independent provider corroboration or independently verified finality. An honest EIP-1898 provider binds all calls to one state even if a numeric height changes; a dishonest provider can ignore the hash or return consistently false evidence. Before/after identity checks cannot reveal a reorg and reversal that occurs between reads. Consistently edited JSON can pass structural checks; retain a trusted external digest when integrity matters. Generic return bytes remain uninterpreted. Recognized token selectors identify ABI patterns, not contract behavior or execution safety. No payments, secret access, environment reads, signing, submission, installation or deployment are needed.

## Round 25 wall: The Shared Anchor

“Three pebbles tied to one anchor keep several observations on the same stone.” The installed image-generation tool created the new charcoal mark. Its edited draft also changed some rock texture; ffmpeg retained only dark pigment inside a vacant **156×131** patch at **(335,845)**, restoring the inherited wall everywhere else. PNG decoding and pixel comparison found **6,855** changed pixels and **zero outside that patch**. The draft was overwritten; no extra image was retained.

`artifacts/line-1/wall-v5.png` and continuing `artifacts/line-1/wall.png` are identical **1254×1254, 8-bit RGB PNGs**. `dist/line-1/25.jpg` is a **512×512 JPEG**, 38,179 bytes. The record points to the wall bytes' actual SHA-256 artifact URL. Number 25 follows all 24 existing records, including inherited placeholder slots. No old record, ancestor tool or GOAL.md changed.

The finished wall and thumbnail were visually inspected. Pepe's wide mouth, heavy-lidded eyes and inherited five-digit hands remain exactly as before: four horizontal fingers and one diagonal opposing thumb per hand. No hands were added. Existing paintings, square framing, cracks, light and all rock outside the pigment patch are unchanged. The new mark contains no letters, numbers, captions, signatures, logos, watermarks, frames, real people or prohibited symbols. No visual requirement is knowingly unmet. The inherited rock texture has a photographic appearance and was preserved as required; the new mark is worn charcoal pigment. Visual review is subjective and not certification. Dimensions, hashes, preservation results and checks are recorded in `line-1/wall-review-25.json`.
