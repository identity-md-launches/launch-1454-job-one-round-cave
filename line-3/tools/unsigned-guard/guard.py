#!/usr/bin/env python3
"""Compare an unsigned type-2 envelope with caller-declared offline expectations."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "erc20-intent"))
import intent


def decimal(text):
    """Parse a bounded unsigned decimal, without signs or alternate bases."""
    if not isinstance(text, str) or not text or any(c not in "0123456789" for c in text):
        raise ValueError("expected an unsigned decimal integer")
    if len(text) > 78 or (len(text) > 1 and text[0] == "0"):
        raise ValueError("decimal integer must be canonical and at most 256 bits")
    number = int(text)
    if number > intent.UINT256_MAX:
        raise ValueError("integer exceeds 256 bits")
    return number


def address(text):
    if not isinstance(text, str) or len(text) != 42 or not text.startswith("0x"):
        raise ValueError("expected a 20-byte 0x-prefixed destination address")
    if any(c not in "0123456789abcdefABCDEF" for c in text[2:]):
        raise ValueError("destination address is not hexadecimal")
    return text.lower()


def destination(text):
    """Explicitly distinguish contract creation from an addressed call."""
    return None if text == "creation" else address(text)


def hex_data(text):
    if not isinstance(text, str) or not text.startswith("0x"):
        raise ValueError("expected 0x-prefixed calldata hex")
    value = text[2:]
    if len(value) > 2 * intent.decoder.MAX_TRANSACTION_BYTES or len(value) % 2:
        raise ValueError("calldata must have even length within 128 KiB")
    if any(c not in "0123456789abcdefABCDEF" for c in value):
        raise ValueError("calldata is not hexadecimal")
    return text.lower()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate access-list JSON key")
        result[key] = value
    return result


def expected_access_list(raw):
    if not isinstance(raw, str) or len(raw) > 2 * intent.decoder.MAX_TRANSACTION_BYTES:
        raise ValueError("access-list JSON exceeds the input limit")
    try:
        items = json.loads(raw, object_pairs_hook=unique_object)
    except json.JSONDecodeError as error:
        raise ValueError("invalid access-list JSON") from error
    if not isinstance(items, list):
        raise ValueError("access-list JSON must be an array")
    expected = []
    for entry in items:
        if not isinstance(entry, dict) or set(entry) != {"address", "storageKeys"}:
            raise ValueError("access-list entries need address and storageKeys only")
        account = address(entry["address"])
        slots = entry["storageKeys"]
        if not isinstance(slots, list):
            raise ValueError("storageKeys must be an array")
        clean_slots = []
        for slot in slots:
            if not isinstance(slot, str) or len(slot) != 66 or not slot.startswith("0x"):
                raise ValueError("storage key must be 32-byte 0x-prefixed hex")
            if any(c not in "0123456789abcdefABCDEF" for c in slot[2:]):
                raise ValueError("storage key is not hexadecimal")
            clean_slots.append(slot.lower())
        expected.append({"address": account, "storageKeys": clean_slots})
    return expected


def check(transaction_hex, expectations):
    """Inspect original bytes, then compare every unsigned field against policy."""
    inspected = intent.interpret(transaction_hex)
    tx = inspected["transaction"]
    raw = bytes.fromhex(transaction_hex[2:] if transaction_hex.startswith("0x") else transaction_hex)
    rules = (
        ("chainId", str(expectations["chainId"]), tx["chainId"], "equal"),
        ("nonce", str(expectations["nonce"]), tx["nonce"], "equal"),
        ("to", expectations["to"], tx["to"], "equal"),
        ("value", str(expectations["value"]), tx["value"], "equal"),
        ("data", expectations["data"], tx["data"], "equal"),
        ("gasLimit", str(expectations["gasLimit"]), tx["gasLimit"], "equal"),
        ("maxPriorityFeePerGas", str(expectations["maxPriorityFeePerGas"]),
         tx["maxPriorityFeePerGas"], "at-most"),
        ("maxFeePerGas", str(expectations["maxFeePerGas"]), tx["maxFeePerGas"], "at-most"),
        ("accessList", expectations["accessList"], tx["accessList"], "equal"),
    )
    checks = []
    for field, expected, actual, relation in rules:
        matched = actual == expected if relation == "equal" else int(actual) <= int(expected)
        checks.append({"field": field, "relation": relation, "expected": expected,
                       "actual": actual, "matched": matched})
    # These are structural consistency conditions in addition to caller's caps.
    checks.append({"field": "priorityWithinFeeCap", "relation": "at-most",
                   "expected": tx["maxFeePerGas"], "actual": tx["maxPriorityFeePerGas"],
                   "matched": int(tx["maxPriorityFeePerGas"]) <= int(tx["maxFeePerGas"])})
    for field in ("chainId", "nonce", "gasLimit", "value", "maxPriorityFeePerGas", "maxFeePerGas"):
        checks.append({"field": field + "WithinUint256", "relation": "at-most",
                       "expected": str(intent.UINT256_MAX), "actual": tx[field],
                       "matched": int(tx[field]) <= intent.UINT256_MAX})
    mismatches = [item for item in checks if not item["matched"]]
    return {
        "status": "matches-expectations" if not mismatches else "mismatch",
        "fingerprint": {"sha256": hashlib.sha256(raw).hexdigest(), "byteLength": len(raw),
                        "meaning": "SHA-256 of unsigned bytes, not an Ethereum transaction hash"},
        "checks": checks,
        "mismatches": mismatches,
        "inspection": inspected,
        "limits": ["Offline structural comparison only; no sender, balance, chain state, execution or safety to sign is established.",
                   "The declared expectations must come from a trusted human decision; this tool cannot judge their intent.",
                   "ABI selector matches do not establish token contract behavior."],
    }


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("transaction", nargs="?", help="complete unsigned 0x02... envelope")
    cli.add_argument("--demo", action="store_true", help="inspect a synthetic ZTO totalSupply() example")
    cli.add_argument("--chain-id")
    cli.add_argument("--nonce")
    cli.add_argument("--to", help="20-byte 0x address, or 'creation' for contract creation")
    cli.add_argument("--value-wei")
    cli.add_argument("--data")
    cli.add_argument("--gas-limit")
    cli.add_argument("--max-priority-fee-per-gas-wei")
    cli.add_argument("--max-fee-per-gas-wei")
    cli.add_argument("--access-list-json", default="[]", help="exact ordered JSON array; defaults to empty")
    return cli


def main(argv):
    cli = parser()
    args = cli.parse_args(argv)
    names = ("chain_id", "nonce", "to", "value_wei", "data", "gas_limit",
             "max_priority_fee_per_gas_wei", "max_fee_per_gas_wei")
    if args.demo:
        if args.transaction is not None or any(getattr(args, name) is not None for name in names) or args.access_list_json != "[]":
            cli.error("--demo cannot be combined with a transaction or expectations")
        transaction = intent.decoder.demo_transaction()
        expected = {"chainId": 1, "nonce": 0, "to": intent.decoder.ZTO,
                    "value": 0, "data": "0x18160ddd", "gasLimit": 100000,
                    "maxPriorityFeePerGas": 1000000000, "maxFeePerGas": 2000000000,
                    "accessList": []}
    else:
        if args.transaction is None:
            cli.error("a complete unsigned transaction is required")
        missing = [name.replace("_", "-") for name in names if getattr(args, name) is None]
        if missing:
            cli.error("missing expectations: " + ", ".join(missing))
        transaction = args.transaction
        expected = {"chainId": decimal(args.chain_id), "nonce": decimal(args.nonce),
                    "to": destination(args.to), "value": decimal(args.value_wei),
                    "data": hex_data(args.data), "gasLimit": decimal(args.gas_limit),
                    "maxPriorityFeePerGas": decimal(args.max_priority_fee_per_gas_wei),
                    "maxFeePerGas": decimal(args.max_fee_per_gas_wei),
                    "accessList": expected_access_list(args.access_list_json)}
    report = check(transaction, expected)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "matches-expectations" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from None
