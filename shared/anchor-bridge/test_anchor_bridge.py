#!/usr/bin/env python3
"""Offline tests for anchor_bridge.py."""
import contextlib
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import anchor_bridge as bridge


def samples():
    digest = "0x" + "ab" * 32
    snapshot = {"anchor": {"hash": digest, "number": "0x2a"}}
    window = {"chain_id": 1, "provider_result": "validated", "to_block": 42,
              "to_block_anchor": {"hash": digest, "number": 42}, "token": "ZTO",
              "token_address": "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e", "transfer_count": 0}
    return snapshot, window


def main():
    snapshot, window = samples()
    receipt = bridge.link(snapshot, window, "one", "two")
    assert receipt["shared_anchor"]["number"] == 42
    assert receipt["token"] == "ZTO"
    try:
        bridge.link(snapshot, dict(window, to_block=43), "", "")
        raise AssertionError("range conflict accepted")
    except bridge.Invalid:
        pass
    try:
        bridge.link(snapshot, dict(window, to_block_anchor={"hash": "0x"+"cd"*32, "number": 42}), "", "")
        raise AssertionError("mismatched hashes accepted")
    except bridge.Invalid:
        pass
    old_snapshot = {"block": snapshot["anchor"]}
    assert bridge.link(old_snapshot, window)["shared_anchor"]["hash"] == snapshot["anchor"]["hash"]
    root = Path("test/scratch/anchor-bridge")
    root.mkdir(parents=True, exist_ok=True)
    try:
        sp, wp = root / "snapshot.json", root / "window.json"
        sp.write_text(json.dumps(snapshot)); wp.write_text(json.dumps(window))
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            assert bridge.main(["link", str(sp), str(wp)]) == 0
        assert json.loads(output.getvalue())["schema"] == "pepeolithic-anchor-bridge/1"
        sp.write_text('{"a":1,"a":2}')
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            assert bridge.main(["link", str(sp), str(wp)]) == 2
        assert not output.getvalue() and "anchor bridge:" in errors.getvalue()
    finally:
        for path in root.glob("*"):
            path.unlink()
        root.rmdir()
    print("5 offline anchor-bridge checks passed")


if __name__ == "__main__":
    main()
