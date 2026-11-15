#!/usr/bin/env python3
"""Stage the tested Settings-linked hall service in an unpacked ROM tree."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


SCRIPT_SHA256 = "fdad1c5be96d99c1528c90860f334c3389033fa69cd9725aa8393aadf2b9736f"


def ensure_line(path: Path, line: str) -> None:
    data = path.read_text(encoding="utf-8")
    if line not in data.splitlines():
        with path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(line + "\n")


def stage(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f"refusing to overwrite differing {path}")
    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip", type=Path)
    parser.add_argument("worktree", type=Path)
    args = parser.parse_args()
    with ZipFile(args.zip) as archive:
        script = archive.read("system/etc/fixo/hall-cover.sh")
        rc = archive.read("rom/fixo-hall-cover.rc")
    if hashlib.sha256(script).hexdigest() != SCRIPT_SHA256:
        raise ValueError("hall script hash changed")
    expected = (b"user system\n" in rc and b"seclabel u:r:shell:s0\n" in rc
                and b"on property:sys.boot_completed=1\n" in rc)
    if not expected:
        raise ValueError("hall init identity or trigger changed")
    root = args.worktree / "filesystems/system_a/system_a/system"
    stage(root / "etc/fixo/hall-cover.sh", script)
    stage(root / "etc/init/fixo-hall-cover.rc", rc)
    cfg = args.worktree / "filesystems/system_a/config"
    for name, mode in (("etc/fixo/hall-cover.sh", "0755"),
                       ("etc/init/fixo-hall-cover.rc", "0644")):
        ensure_line(cfg / "system_a_fs_config", f"system_a/system/{name} 0 0 {mode}")
        escaped = name.replace(".", r"\.")
        line = f"/system_a/system/{escaped} u:object_r:system_file:s0"
        ensure_line(cfg / "system_a_file_contexts", line)
        ensure_line(cfg / "system_a_file_contexts.build-ascii", line)
    print("staged hall script and init RC")


if __name__ == "__main__":
    main()
