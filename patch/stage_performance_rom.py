#!/usr/bin/env python3
"""Stage the already tested Settings -> PowerManager bridge for ROM init."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


SOURCE_SHA256 = "52c426336c8af2d6631ec7435b05f5ec72f920aa18e789deeab95eafc1af469b"

RC = """on property:sys.boot_completed=1
    start fixo_performance

service fixo_performance /system/bin/sh /system/etc/fixo/performance.sh
    class late_start
    disabled
    user shell
    group shell system log
    seclabel u:r:shell:s0
""".encode()


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
    parser.add_argument("module_zip", type=Path)
    parser.add_argument("worktree", type=Path)
    args = parser.parse_args()
    if hashlib.sha256(args.module_zip.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("Settings companion module changed")
    with ZipFile(args.module_zip) as archive:
        original = archive.read("high_performance_bridge.sh")
    if b"su -Z u:r:shell:s0 2000 -c" not in original:
        raise ValueError("expected tested shell identity missing")
    script = original.replace(
        b"su -Z u:r:shell:s0 2000 -c \"$1\"",
        b"/system/bin/sh -c \"$1\"",
    )
    if b"su -Z" in script or script == original:
        raise ValueError("failed to convert Magisk bridge to init shell identity")
    root = args.worktree / "filesystems/system_a/system_a/system"
    stage(root / "etc/fixo/performance.sh", script)
    stage(root / "etc/init/fixo-performance.rc", RC)
    cfg = args.worktree / "filesystems/system_a/config"
    for name, mode in (("etc/fixo/performance.sh", "0755"),
                       ("etc/init/fixo-performance.rc", "0644")):
        ensure_line(cfg / "system_a_fs_config", f"system_a/system/{name} 0 0 {mode}")
        escaped = name.replace(".", r"\.")
        line = f"/system_a/system/{escaped} u:object_r:system_file:s0"
        ensure_line(cfg / "system_a_file_contexts", line)
        ensure_line(cfg / "system_a_file_contexts.build-ascii", line)
    print("staged tested performance bridge and init RC")


if __name__ == "__main__":
    main()
