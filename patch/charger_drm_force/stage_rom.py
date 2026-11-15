#!/usr/bin/env python3
"""Stage the tested charger payload into a copied ROM filesystem tree."""

import argparse
import hashlib
import shutil
from pathlib import Path


STOCK_SHA = "a4b3e3e9d37c779ffa5dced09c4faf2bf0b83cdc624b4dc06a31ef6d5f137f03"
PATCHED_SHA = "ca444a23efa4e760d23506df4e09c5249df05a9c265e9928f6844338cfae12b5"
HELPER_SHA = "8c36c4469332508b3c5e99381d6380b8ed4c33f5e7db70703f7e697c47070bc8"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, line: str) -> None:
    data = path.read_text(encoding="utf-8")
    if line in data.splitlines():
        return
    with path.open("a", encoding="utf-8", newline="\n") as out:
        if not data.endswith("\n"):
            out.write("\n")
        out.write(line + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", type=Path, help="Copied v5-build/filesystems/system_a")
    parser.add_argument("verbose_charger", type=Path)
    parser.add_argument("helper", type=Path)
    args = parser.parse_args()

    root = args.tree / "system_a/system"
    stock = root / "bin/charger"
    if digest(stock) != STOCK_SHA:
        raise ValueError("Unexpected ROM charger; do not overwrite it")
    if digest(args.verbose_charger) != PATCHED_SHA or digest(args.helper) != HELPER_SHA:
        raise ValueError("Payload hash mismatch")

    source = Path(__file__).resolve().parent
    script = source / "rom-charger-watch.sh"
    body = script.read_bytes()
    if b"sleep 60" in body or b"/data/adb" in body:
        raise ValueError("ROM script contains a Magisk path or auto-wake timer")

    backup = args.tree.parent.parent / "originals-before-v5/charger.original"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(stock, backup)
    shutil.copyfile(args.verbose_charger, stock)
    shutil.copyfile(args.helper, root / "bin/charger_drm_blank")
    (root / "etc/fixo").mkdir(parents=True, exist_ok=True)
    (root / "etc/fixo/charger-watch.sh").write_bytes(body)
    (root / "etc/init/fixo-charger.rc").write_bytes((source / "rom-charger.rc").read_bytes())

    config = args.tree / "config/system_a_fs_config"
    contexts = args.tree / "config/system_a_file_contexts"
    for line in (
        "system_a/system/bin/charger_drm_blank 0 0 0755",
        "system_a/system/etc/fixo 0 0 0755",
        "system_a/system/etc/fixo/charger-watch.sh 0 0 0755",
        "system_a/system/etc/init/fixo-charger.rc 0 0 0644",
    ):
        append_once(config, line)
    for line in (
        "/system_a/system/bin/charger_drm_blank u:object_r:charger_exec:s0",
        "/system_a/system/etc/fixo/charger-watch\\.sh u:object_r:system_file:s0",
        "/system_a/system/etc/init/fixo-charger\\.rc u:object_r:system_file:s0",
    ):
        append_once(contexts, line)

    assert digest(stock) == PATCHED_SHA
    assert digest(root / "bin/charger_drm_blank") == HELPER_SHA
    print(f"Staged charger and watcher under {root}")
    print(f"Stock backup: {backup}")


if __name__ == "__main__":
    main()
