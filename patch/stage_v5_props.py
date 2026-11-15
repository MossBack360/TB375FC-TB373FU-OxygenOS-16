#!/usr/bin/env python3
"""Merge confirmed Magisk system.prop values into the v5 ROM property files."""

import argparse
from pathlib import Path


def properties(path: Path) -> dict[str, set[str]]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result.setdefault(key, set()).add(value)
    return result


def require(path: Path, wanted: dict[str, str]) -> None:
    existing = properties(path)
    for key, value in wanted.items():
        if existing.get(key) != {value}:
            raise ValueError(f"{path}: expected {key}={value}, got {existing.get(key)!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("work", type=Path)
    parser.add_argument("vendor_reference", type=Path)
    args = parser.parse_args()
    root = args.work / "filesystems" / "system_a" / "system_a"
    system = root / "system" / "build.prop"
    # Already integrated in the v4 baseline. Do not add duplicates elsewhere.
    require(system, {"debug.camera.morpho.sr.on": "0"})
    require(root / "my_product" / "build.prop", {"ro.oplus.display.rc.size": "26,26,26,26"})
    require(root / "my_manifest" / "build.prop", {
        "ro.product.model": "Lenovo Xiaoxin Pad Pro 12.7 (2025)",
        "ro.vendor.oplus.market.name": "Lenovo Xiaoxin Pad Pro 12.7 (2025)",
    })
    require(args.vendor_reference / "build.prop", {"ro.audio.monitorRotation": "true"})

    additions = {
        "persist.sys.oplus.nandswap.storage.min": "19",
        "ro.build.release_type": "true",
        "persist.vendor.radio.virtualcomm": "1",
        "persist.vendor.radio.virtualcomm.enable": "1",
    }
    existing = properties(system)
    new = []
    for key, value in additions.items():
        old = existing.get(key)
        if old is None:
            new.append(f"{key}={value}")
        elif old != {value}:
            raise ValueError(f"Conflicting {key}={old} in {system}")
    if new:
        with system.open("a", encoding="utf-8", newline="\n") as out:
            out.write("\n# FixO integrated static module properties\n")
            out.write("\n".join(new) + "\n")
    require(system, additions)
    report = args.work / "staged-static-props.txt"
    report.write_text("Already present: camera SR, 26px corner, device model, vendor audio rotation\n"
                      + "Added or confirmed in system/build.prop:\n"
                      + "\n".join(f"{k}={v}" for k, v in additions.items()) + "\n",
                      encoding="utf-8")
    print(f"Added {len(new)} properties; {report}")


if __name__ == "__main__":
    main()
