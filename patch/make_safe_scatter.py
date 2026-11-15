#!/usr/bin/env python3
"""Restrict the v5 flash metadata to super only."""

import argparse
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


ALLOW = {"super"}
NAMES = ("MT6897_Android_scatter.txt", "MT6897_Android_scatter.xml")


def patch_text(path: Path) -> dict[str, int]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    current = None
    seen: dict[str, int] = {}
    output = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("partition_name:"):
            current = stripped.split(":", 1)[1].strip()
            seen[current] = seen.get(current, 0) + 1
        if stripped.startswith("is_download:") and current:
            line = line.replace(stripped, "is_download: " + str(current in ALLOW).lower(), 1)
        output.append(line)
    path.write_text("".join(output), encoding="utf-8")
    return seen


def patch_xml(path: Path) -> dict[str, int]:
    tree = ET.parse(path)
    seen: dict[str, int] = {}
    for part in tree.iter("partition_index"):
        name = part.findtext("partition_name")
        flag = part.find("is_download")
        if name and flag is not None:
            seen[name] = seen.get(name, 0) + 1
            flag.text = str(name in ALLOW).lower()
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return seen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image_dir", type=Path)
    parser.add_argument("backup_dir", type=Path, nargs="?")
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()
    if not args.in_place:
        if args.backup_dir is None:
            parser.error("backup_dir is required unless --in-place is set")
        args.backup_dir.mkdir(parents=True, exist_ok=True)
    counts = []
    for name, patch in zip(NAMES, (patch_text, patch_xml)):
        path = args.image_dir / name
        if not args.in_place:
            shutil.copyfile(path, args.backup_dir / name)
        counts.append(patch(path))
    for seen in counts:
        assert all(seen.get(name, 0) > 0 for name in ALLOW)
        assert seen.get("preloader_a", 0) > 0 and seen.get("preloader_b", 0) > 0
    assert counts[0] == counts[1], "Text and XML scatter partition sets differ"
    for name in NAMES:
        text = (args.image_dir / name).read_text(encoding="utf-8")
        assert "preloader_a" in text and "preloader_b" in text
    print("Restricted scatter to:", ", ".join(sorted(ALLOW)))
    if not args.in_place:
        print("Originals:", args.backup_dir)


if __name__ == "__main__":
    main()
