#!/usr/bin/env python3
"""Build a reversible same-device ColorOS charger A/B module."""

from pathlib import Path
import hashlib
import sys
import zipfile

SOURCE_SHA256 = "09b3c8796ca09b311bab84fee97455a995643e2f8bb36fc3911a6265091a544f"


def main() -> None:
    src, out = map(Path, sys.argv[1:3])
    payload = src.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == SOURCE_SHA256
    assert payload.startswith(b"\x7fELF")
    out.parent.mkdir(parents=True, exist_ok=True)
    prop = """id=fixo_charger_verbose_trial
name=TB375FC ColorOS Charger A/B Trial
version=0.2-coloros-test
versionCode=2
author=MossBack360
description=Temporary same-device ColorOS 16.0.7 off-mode charger binary comparison.
"""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("module.prop", prop)
        z.writestr("system/bin/charger", payload)
    with zipfile.ZipFile(out) as z:
        assert set(z.namelist()) == {"module.prop", "system/bin/charger"}
        assert all("\\" not in name for name in z.namelist())
        assert hashlib.sha256(z.read("system/bin/charger")).hexdigest() == SOURCE_SHA256
    print(out)


if __name__ == "__main__":
    main()
