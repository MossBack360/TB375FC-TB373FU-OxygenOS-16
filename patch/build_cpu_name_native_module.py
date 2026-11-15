#!/usr/bin/env python3
"""Package the tested-offline CPU-name XML as a reversible Magisk trial."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


EXPECTED = "52337617affadbf873d42e3617ef5d248c62671ed7597b163a96a402d44125db"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config_xml", type=Path)
    parser.add_argument("output_zip", type=Path)
    args = parser.parse_args()
    xml = args.config_xml.read_bytes()
    if hashlib.sha256(xml).hexdigest() != EXPECTED:
        raise ValueError("CPU config XML changed")
    args.output_zip.parent.mkdir(parents=True, exist_ok=True)
    if args.output_zip.exists():
        raise FileExistsError(args.output_zip)
    script = """#!/system/bin/sh
src=${0%/*}/payload/config_processor_com.android.settings.xml
dst=/my_stock/etc/extension/config_processor_com.android.settings.xml
[ -f "$src" ] && [ -f "$dst" ] || exit 1
chmod 0644 "$src" || exit 1
chcon u:object_r:system_file:s0 "$src" || exit 1
mount --bind "$src" "$dst"
"""
    entries = {
        "module.prop": b"id=fixo_cpu_name_native\nname=TB375FC native CPU name\nversion=0.1-test\nversionCode=1\nauthor=MossBack360\ndescription=Stock Settings CPU mapping for Dimensity 8300.\n",
        "system.prop": b"ro.product.cpuinfo=MT6897-TB375FC\n",
        "post-fs-data.sh": script.encode(),
        "payload/config_processor_com.android.settings.xml": xml,
    }
    with ZipFile(args.output_zip, "w", ZIP_DEFLATED) as out:
        for name, data in entries.items():
            out.writestr(name, data)
    with ZipFile(args.output_zip) as check:
        assert set(check.namelist()) == set(entries)
        assert not any("\\" in name for name in check.namelist())
    print(args.output_zip)


if __name__ == "__main__":
    main()
