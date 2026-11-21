# Derived from Mornye-Extension (https://github.com/mornyeapp/Mornye-Extension), Copyright 2026 zarzet, LGPL-3.0-only. Modified for Kalao.
"""Validate index.json against every package, including packages without a source."""

import base64
import hashlib
import json
import os
import unittest
from pathlib import Path
from zipfile import ZipFile

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except ImportError:  # signatures are then checked only in CI
    Ed25519PublicKey = None


ROOT = Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))


def decode(value):
    if not value.startswith("ed25519:"):
        raise ValueError("expected ed25519:<base64>")
    return base64.b64decode(value[len("ed25519:"):], validate=True)


class IndexPackagesTest(unittest.TestCase):
    def test_index_has_a_name_and_key(self):
        self.assertTrue(INDEX["name"].strip())
        self.assertEqual(len(decode(INDEX["publicKey"])), 32)

    def test_entries_match_their_packages(self):
        entries = INDEX["extensions"]
        self.assertEqual(len(entries), len({(entry["id"], entry["version"]) for entry in entries}))
        for entry in entries:
            with self.subTest(extension=entry["id"]):
                self.assertTrue(entry["url"].startswith("extensions/"), entry["url"])
                self.assertTrue(entry["url"].endswith(".kalaoext"), entry["url"])
                data = (ROOT / entry["url"]).read_bytes()
                self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
                with ZipFile(ROOT / entry["url"]) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertIn("index.js", archive.namelist())
                    manifest = json.loads(archive.read("manifest.json"))
                self.assertEqual(entry["id"], manifest["id"])
                self.assertEqual(entry["version"], manifest["version"])
                self.assertEqual(entry.get("minKalao"), manifest.get("minKalao"))

    def test_every_package_is_listed(self):
        listed = {entry["url"] for entry in INDEX["extensions"]}
        packages = {f"extensions/{path.name}" for path in (ROOT / "extensions").glob("*.kalaoext")}
        self.assertEqual(packages, listed)

    def test_every_source_has_a_package(self):
        for source in sorted(path for path in (ROOT / "sources").iterdir() if path.is_dir()):
            with self.subTest(source=source.name):
                self.assertTrue((ROOT / "extensions" / f"{source.name}.kalaoext").exists())

    def test_signatures_verify_against_the_repository_key(self):
        if Ed25519PublicKey is None:
            if os.environ.get("CI"):
                self.fail("install 'cryptography' to verify signatures")
            self.skipTest("'cryptography' is not installed")
        key = Ed25519PublicKey.from_public_bytes(decode(INDEX["publicKey"]))
        for entry in INDEX["extensions"]:
            with self.subTest(extension=entry["id"]):
                try:
                    key.verify(decode(entry["signature"]), (ROOT / entry["url"]).read_bytes())
                except InvalidSignature:
                    self.fail(f"{entry['id']}: signature does not match the repository key")


if __name__ == "__main__":
    unittest.main()
