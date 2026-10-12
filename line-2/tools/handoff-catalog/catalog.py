#!/usr/bin/env python3
"""Create and replay a deterministic, offline catalog of HANDOFF v1 archives."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import zipfile


FORMAT = "handoff-catalog-v1"
INSPECTOR = Path("line-2/tools/handoff-inspect/inspect_handoff.py")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + repr(key))
        result[key] = value
    return result


def workspace_file(raw, must_exist=True):
    """Resolve one ordinary relative workspace file without following links."""
    if not isinstance(raw, str) or not raw or raw == ".":
        raise ValueError("use a nonempty relative workspace file")
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("use a relative workspace path without '..'")
    current = Path.cwd()
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlinks are not allowed: " + raw)
    if must_exist:
        info = current.stat(follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("not a regular file: " + raw)
    return current


def inspector():
    path = workspace_file(INSPECTOR.as_posix())
    spec = importlib.util.spec_from_file_location("handoff_catalog_inspector", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8") + b"\n"


def summary(path, receipt):
    return {"path": path, "sha256": receipt["archive_sha256"],
            "bytes": receipt["archive_bytes"], "files": receipt["file_count"],
            "payload_bytes": receipt["payload_bytes"]}


def build(paths, check=None):
    """Inspect every named archive and return a canonical catalog object."""
    if not paths:
        raise ValueError("at least one archive is required")
    check = check or inspector()
    names = []
    for raw in paths:
        path = workspace_file(raw)
        names.append(path.relative_to(Path.cwd()).as_posix())
    if len(set(names)) != len(names):
        raise ValueError("archive paths must be distinct")
    archives = [summary(name, check.inspect_path(name)) for name in sorted(names)]
    return {"format": FORMAT, "archives": archives}


def parse_catalog(data):
    value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=lambda x: (_ for _ in ()).throw(
                           ValueError("non-standard JSON constant: " + x)))
    if not isinstance(value, dict) or set(value) != {"format", "archives"}:
        raise ValueError("unsupported catalog shape")
    if value["format"] != FORMAT or not isinstance(value["archives"], list) or not value["archives"]:
        raise ValueError("unsupported catalog")
    previous = ""
    for item in value["archives"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "bytes", "files", "payload_bytes"}:
            raise ValueError("invalid catalog entry")
        path, digest = item["path"], item["sha256"]
        if (not isinstance(path, str) or path <= previous or not isinstance(digest, str)
                or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
                or any(type(item[key]) is not int or item[key] < 0
                       for key in ("bytes", "files", "payload_bytes"))):
            raise ValueError("invalid or unsorted catalog entry")
        workspace_file(path)
        previous = path
    if canonical(value) != data:
        raise ValueError("catalog is not canonical JSON")
    return value


def verify(data, check=None):
    """Replay each pinned receipt; return only after every archive verifies."""
    value = parse_catalog(data)
    check = check or inspector()
    actual = []
    for expected in value["archives"]:
        receipt = check.inspect_path(expected["path"], expected=expected["sha256"])
        found = summary(expected["path"], receipt)
        if found != expected:
            raise ValueError("catalog receipt changed: " + expected["path"])
        actual.append(found)
    return {"format": FORMAT, "verified": True, "archives": actual,
            "note": "Archive integrity is not sender identity without independently trusted digests."}


def exclusive_write(raw, data):
    target = workspace_file(raw, must_exist=False)
    if target.exists():
        raise ValueError("refusing to overwrite existing catalog")
    with target.open("xb") as stream:
        stream.write(data)


def demo():
    value = build(["line-2/handoff.zip"])
    result = verify(canonical(value))
    result["demo"] = "real inherited archive cataloged and replayed in memory"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo")
    make = commands.add_parser("make")
    make.add_argument("output", help="new catalog path inside this workspace")
    make.add_argument("archives", nargs="+", help="relative HANDOFF v1 ZIP paths")
    replay = commands.add_parser("verify")
    replay.add_argument("catalog", help="relative catalog path inside this workspace")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            result = demo()
        elif args.command == "make":
            value = build(args.archives)
            data = canonical(value)
            exclusive_write(args.output, data)
            result = {"format": FORMAT, "created": args.output,
                      "archives": value["archives"]}
        else:
            result = verify(workspace_file(args.catalog).read_bytes())
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError,
            zipfile.BadZipFile, EOFError) as error:
        print("handoff-catalog: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
