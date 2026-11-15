#!/usr/bin/env python3
"""Fail closed unless a v5 SP Flash Tool package targets only approved images."""

import argparse
import configparser
from pathlib import Path
import xml.etree.ElementTree as ET


ALLOW = {"super": "super.img"}


def scatter_xml(path: Path) -> dict[str, set[tuple[str, str]]]:
    seen = {}
    for item in ET.parse(path).iter("partition_index"):
        name = item.findtext("partition_name")
        if not name:
            continue
        seen.setdefault(name, set()).add((item.findtext("is_download"), item.findtext("file_name")))
    return seen


def scatter_text(path: Path) -> dict[str, set[tuple[str, str]]]:
    seen = {}
    current = {}
    for raw in path.read_text(encoding="utf-8").splitlines() + ["- partition_index: END"]:
        line = raw.strip()
        if line.startswith("- partition_index:"):
            name = current.get("partition_name")
            if name:
                seen.setdefault(name, set()).add((current.get("is_download"), current.get("file_name")))
            current = {}
        elif ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    return seen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--allow-missing-super", action="store_true")
    args = parser.parse_args()
    image = args.package / "image"
    txt = scatter_text(image / "MT6897_Android_scatter.txt")
    xml = scatter_xml(image / "MT6897_Android_scatter.xml")
    if txt != xml:
        raise ValueError("Text and XML scatter disagree")
    for name in ("preloader_a", "preloader_b"):
        if name not in xml:
            raise ValueError(f"Missing {name} audit entry")
    for name, values in xml.items():
        expected = "true" if name in ALLOW else "false"
        for flag, filename in values:
            if flag != expected:
                raise ValueError(f"Unsafe {name} row: {flag}, {filename}")
            if name in ALLOW and filename != ALLOW[name]:
                raise ValueError(f"Unexpected {name} payload: {filename}")
    enabled = {name: ALLOW[name] for name in ALLOW if name in xml}
    if enabled != ALLOW:
        raise ValueError(f"Unsafe enabled partitions: {enabled}")
    for part, filename in enabled.items():
        if part == "super" and args.allow_missing_super:
            continue
        if not (image / filename).is_file():
            raise ValueError(f"Missing payload: {filename}")
    flash = ET.parse(image / "download_agent" / "flash.xml")
    if flash.findtext("scatter") != "../MT6897_Android_scatter.xml":
        raise ValueError("flash.xml points to another scatter")
    options = configparser.ConfigParser()
    options.read(args.package / "tool" / "option.ini", encoding="utf-8")
    scene = options["DownloadScene"]
    if (scene.get("Format_All_Download"), scene.get("Firmware_Upgrade"),
            scene.get("Download_Only")) != ("false", "false", "true"):
        raise ValueError(f"Unsafe SP Flash Tool defaults: {dict(scene)}")
    if (args.package / "tool" / "history.ini").exists():
        raise ValueError("Stale flash tool history.ini could reopen an old scatter")
    print("Flash allowlist: super only; init_boot and preloader disabled; Download Only default")


if __name__ == "__main__":
    main()
