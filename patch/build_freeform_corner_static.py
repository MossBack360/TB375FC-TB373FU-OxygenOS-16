#!/usr/bin/env python3
"""Repack the confirmed corner feature without the obsolete mode poller."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse


def unique(folder: Path, prefix: str) -> Path:
    matches = list(folder.glob(prefix + "*.zip"))
    if len(matches) != 1:
        raise ValueError(matches)
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stable", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    active = args.stable / "01-当前启用-Magisk"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    with ZipFile(unique(active, "10-")) as old, ZipFile(unique(active, "05-")) as ai:
        mount = old.read("post-fs-data.sh")
        feature = ai.read("payload/com.oplus.oplus-feature.xml")
    metadata = """id=fixo_freeform_corner_gesture
name=FixO Freeform Corner Gesture
version=v1.4-static-only
versionCode=6
author=MossBack360
description=Unified corner feature table; no obsolete three-mode service.
"""
    readme = """Retains the v1.3 post-fs-data feature-file bind.
Uses the v2.9 unified feature XML, which includes freeform, AI and virtualmodem gates.
No service.sh: the old three-mode corner/assistant poller is intentionally omitted.
"""
    entries = {
        "module.prop": metadata.encode(),
        "README.txt": readme.encode(),
        "post-fs-data.sh": mount,
        "payload/com.oplus.oplus-feature.xml": feature,
        "system/my_product/etc/extension/com.oplus.oplus-feature.xml": feature,
    }
    with ZipFile(args.output, "w", ZIP_DEFLATED) as out:
        for name, data in entries.items():
            out.writestr(name, data)
    with ZipFile(args.output) as check:
        assert set(check.namelist()) == set(entries)
        assert not any("\\" in name for name in check.namelist())
        assert "service.sh" not in check.namelist()
    print(args.output)


if __name__ == "__main__":
    main()
