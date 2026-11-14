#!/usr/bin/env python3
"""Build a one-instruction charger logging trial with exact-input assertions."""

from pathlib import Path
import hashlib
import sys
import zipfile

SOURCE_SHA256 = "a4b3e3e9d37c779ffa5dced09c4faf2bf0b83cdc624b4dc06a31ef6d5f137f03"
PATCH_OFFSET = 0x1DF0C
OLD = bytes.fromhex("c0 00 80 52")  # mov w0, #6
NEW = bytes.fromhex("e0 00 80 52")  # mov w0, #7


def main() -> None:
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    original = src.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SOURCE_SHA256
    assert original[PATCH_OFFSET : PATCH_OFFSET + 4] == OLD
    patched = bytearray(original)
    patched[PATCH_OFFSET : PATCH_OFFSET + 4] = NEW
    assert sum(a != b for a, b in zip(original, patched)) == 1
    out.parent.mkdir(parents=True, exist_ok=True)
    prop = """id=fixo_charger_verbose_trial
name=TB375FC Charger Verbose Trace Trial
version=0.1-debug
versionCode=1
author=MossBack360
description=Temporary one-instruction charger klog level 6 to 7 diagnostic.
"""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("module.prop", prop)
        z.writestr("system/bin/charger", patched)
    with zipfile.ZipFile(out) as z:
        assert set(z.namelist()) == {"module.prop", "system/bin/charger"}
        assert all("\\" not in name for name in z.namelist())
        assert z.read("system/bin/charger") == patched
    print(f"source={SOURCE_SHA256}")
    print(f"patched={hashlib.sha256(patched).hexdigest()}")
    print(f"zip={out}")


if __name__ == "__main__":
    main()
