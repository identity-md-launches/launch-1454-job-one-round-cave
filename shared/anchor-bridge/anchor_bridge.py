#!/usr/bin/env python3
"""Link a Line 1 block-pinned snapshot to a Line 4 transfer-window anchor.

The program is deliberately offline: it reads two explicit JSON files and writes
only its receipt to stdout.  It never performs RPC, executes payload code, or
opens an output path.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_INPUT = 100_000
HASH = re.compile(r"0x[0-9a-f]{64}\Z")


class Invalid(ValueError):
    pass


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Invalid("duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    root = Path.cwd().resolve()
    candidate = Path(path).resolve()
    if candidate != root and root not in candidate.parents:
        raise Invalid("input path is outside the workspace")
    raw = candidate.read_bytes()
    if not raw or len(raw) > MAX_INPUT:
        raise Invalid("input size is outside bounds")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates,
                           parse_constant=lambda _: (_ for _ in ()).throw(Invalid("non-finite JSON")))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Invalid("invalid JSON") from error
    if not isinstance(value, dict):
        raise Invalid("top-level JSON must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def number(value):
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    if isinstance(value, str) and re.fullmatch(r"0x[0-9a-f]+", value):
        return int(value, 16)
    raise Invalid("anchor number is not canonical")


def anchor_from_snapshot(snapshot):
    # Hash Snapshot v1 has anchor; earlier pinned snapshot has block.
    candidate = snapshot.get("anchor", snapshot.get("block"))
    if not isinstance(candidate, dict):
        raise Invalid("snapshot has no block anchor")
    digest, height = candidate.get("hash"), candidate.get("number")
    if not isinstance(digest, str) or not HASH.fullmatch(digest):
        raise Invalid("snapshot hash is invalid")
    return {"hash": digest, "number": number(height)}


def anchor_from_window(window):
    if window.get("chain_id") != 1 or window.get("provider_result") != "validated":
        raise Invalid("transfer window is not a validated Ethereum mainnet observation")
    candidate = window.get("to_block_anchor")
    if not isinstance(candidate, dict):
        raise Invalid("transfer window has no closing anchor")
    digest, height = candidate.get("hash"), candidate.get("number")
    if not isinstance(digest, str) or not HASH.fullmatch(digest):
        raise Invalid("transfer-window hash is invalid")
    if number(height) != window.get("to_block"):
        raise Invalid("transfer-window closing height conflicts with its range")
    return {"hash": digest, "number": number(height)}


def link(snapshot, window, snapshot_sha256="", window_sha256=""):
    left, right = anchor_from_snapshot(snapshot), anchor_from_window(window)
    if left != right:
        raise Invalid("snapshot and transfer window do not share an exact closing anchor")
    return {
        "schema": "pepeolithic-anchor-bridge/1",
        "chain_id": 1,
        "shared_anchor": left,
        "snapshot_sha256": snapshot_sha256,
        "transfer_window_sha256": window_sha256,
        "token": window.get("token"),
        "token_address": window.get("token_address"),
        "transfer_count": window.get("transfer_count"),
        "limitations": "A shared anchor links these supplied observations only; it does not prove finality, provider honesty, log completeness, token balance, or atomic collection."
    }


def demo():
    digest = "0x" + "ab" * 32
    snapshot = {"anchor": {"hash": digest, "number": "0x2a"}}
    window = {"chain_id": 1, "provider_result": "validated", "to_block": 42,
              "to_block_anchor": {"hash": digest, "number": 42}, "token": "ZTO",
              "token_address": "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e", "transfer_count": 0}
    return link(snapshot, window, "demo-snapshot", "demo-transfer-window")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="print an in-memory, offline linkage receipt")
    link_parser = sub.add_parser("link", help="link explicit snapshot and transfer-window JSON files")
    link_parser.add_argument("snapshot")
    link_parser.add_argument("transfer_window")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            receipt = demo()
        else:
            snapshot, snapshot_digest = read_json(args.snapshot)
            window, window_digest = read_json(args.transfer_window)
            receipt = link(snapshot, window, snapshot_digest, window_digest)
    except (OSError, Invalid) as error:
        print("anchor bridge: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
