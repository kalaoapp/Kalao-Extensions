#!/usr/bin/env python3
# Derived from Mornye-Extension (https://github.com/mornyeapp/Mornye-Extension), Copyright 2026 zarzet, LGPL-3.0-only. Modified for Kalao.
"""Build reproducible source-backed extensions and refresh the signed index.json.

Every directory in sources/ is validated, tested offline against its
fixtures/tests.json and packed with kalao-ext into extensions/<dir>.kalaoext.
index.json is then rebuilt and signed from every package in extensions/,
including package-only submissions.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_NAME = "Kalao Extensions"


def kalao_ext(binary, *args):
    result = subprocess.run([binary, *map(str, args)], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"kalao-ext {' '.join(map(str, args))} failed:\n{result.stdout}{result.stderr}")
    return result.stdout


def build(binary, source, out):
    kalao_ext(binary, "validate", source)
    if (source / "fixtures" / "tests.json").exists():
        kalao_ext(binary, "test", source)
    kalao_ext(binary, "pack", source, "-o", out)
    return out.read_bytes()


def signed_index(binary, key, scratch):
    out = scratch / "index.json"
    kalao_ext(binary, "index", ROOT / "extensions", "--key", key, "--name", REPOSITORY_NAME, "-o", out)
    index = json.loads(out.read_text(encoding="utf-8"))
    # kalao-ext writes package URLs relative to extensions/; index.json lives one level up.
    for entry in index["extensions"]:
        entry["url"] = "extensions/" + entry["url"]
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sources", nargs="*", help="Source directory names (default: all)")
    parser.add_argument("--check", action="store_true", help="Verify packages without writing")
    parser.add_argument("--key", default=os.environ.get("KALAO_REPO_KEY"),
                        help="Repository secret key (default: $KALAO_REPO_KEY); required unless --check")
    parser.add_argument("--kalao-ext", default=os.environ.get("KALAO_EXT", "kalao-ext"),
                        help="kalao-ext binary (default: $KALAO_EXT or kalao-ext on PATH)")
    parser.add_argument("--rotate-key", action="store_true",
                        help="Allow a new repository key; every user must remove and re-add the repository")
    args = parser.parse_args()

    binary = shutil.which(args.kalao_ext) or args.kalao_ext
    if not Path(binary).exists():
        parser.error(f"kalao-ext not found ({args.kalao_ext}); build it from kalaoapp/Kalao or pass --kalao-ext")
    if not args.check and not args.key:
        parser.error("--key (or KALAO_REPO_KEY) is required to sign index.json")

    names = args.sources or sorted(path.name for path in (ROOT / "sources").iterdir() if path.is_dir())
    stale = []
    with tempfile.TemporaryDirectory() as directory:
        scratch = Path(directory)
        # Validate and pack every selected source before writing anything.
        builds = []
        for name in dict.fromkeys(names):
            source = ROOT / "sources" / name
            if Path(name).name != name or name in (".", "..") or not source.is_dir():
                parser.error(f"Invalid source directory: {name}")
            try:
                data = build(binary, source, scratch / f"{name}.kalaoext")
            except RuntimeError as error:
                parser.exit(1, f"{name}: {error}\n")
            builds.append((name, ROOT / "extensions" / f"{name}.kalaoext", data))

        for name, destination, data in builds:
            if destination.exists() and destination.read_bytes() == data:
                continue
            if args.check:
                stale.append(name)
            else:
                destination.write_bytes(data)
                print(f"packed {destination.relative_to(ROOT).as_posix()}")

        if args.check:
            if stale:
                parser.exit(1, "Stale packages (run scripts/build_packages.py --key …): " + ", ".join(stale) + "\n")
            print("packages match their sources")
            return

        index_path = ROOT / "index.json"
        text = signed_index(binary, args.key, scratch)
        if index_path.exists() and not args.rotate_key:
            old_key = json.loads(index_path.read_text(encoding="utf-8")).get("publicKey")
            new_key = json.loads(text)["publicKey"]
            if old_key and old_key != new_key:
                parser.exit(1, "The key does not match index.json's publicKey. A new key blocks updates "
                               "for every user until they re-add the repository; pass --rotate-key if intended.\n")
        if not index_path.exists() or index_path.read_text(encoding="utf-8") != text:
            index_path.write_text(text, encoding="utf-8", newline="\n")
            print("updated index.json")
        else:
            print("index.json is up to date")


if __name__ == "__main__":
    sys.exit(main())
