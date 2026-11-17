#!/usr/bin/env python3
"""Stage the confirmed ASI screen-attention glue as a native init service."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


SOURCE_SHA256 = "cd00183519bd1d603f83d371ddaef3c6ffde5ecc2f7930d03296e898a3692ad7"
OLD_STAGED_SCRIPT_SHA256 = "d53fe747eeda12f70632652f39644a9ba8a0984cc71064a718a0b4200378b4de"
RC = b"""on property:sys.boot_completed=1
    start fixo_attention

service fixo_attention /system/bin/sh /system/etc/fixo/attention.sh
    class late_start
    disabled
    user root
    group root system log camera
    seclabel u:r:shell:s0
"""


def ensure_line(path: Path, line: str) -> None:
    if line not in path.read_text(encoding="utf-8").splitlines():
        with path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(line + "\n")


def stage(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"refusing to overwrite differing {path}")
        return
    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("module_zip", type=Path)
    parser.add_argument("worktree", type=Path)
    args = parser.parse_args()
    if hashlib.sha256(args.module_zip.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("attention module changed")
    with ZipFile(args.module_zip) as archive:
        script = archive.read("service.sh")
        helper = archive.read("attention-useractivity.apk")
    for old, new in (
        (b"MODDIR=${0%/*}\n", b""),
        (b'HELPER="$MODDIR/attention-useractivity.apk"',
         b'HELPER="/system/etc/fixo/attention-useractivity.apk"'),
        (b'LOG="$MODDIR/runtime.log"',
         b'LOG="/data/local/tmp/fixo-attention.log"'),
    ):
        if script.count(old) != 1:
            raise ValueError(f"unexpected attention source: {old!r}")
        script = script.replace(old, new)
    if b"$MODDIR" in script:
        raise ValueError("Magisk path remains")
    system = args.worktree / "filesystems/system_a/system_a/system"
    entries = {
        "etc/fixo/attention.sh": (script, "0755"),
        "etc/fixo/attention-useractivity.apk": (helper, "0644"),
        "etc/init/fixo-attention.rc": (RC, "0644"),
    }
    config = args.worktree / "filesystems/system_a/config"
    for name, (data, mode) in entries.items():
        destination = system / name
        if name == "etc/fixo/attention.sh" and destination.exists() and destination.read_bytes() != data:
            previous = destination.read_bytes()
            if hashlib.sha256(previous).hexdigest() != OLD_STAGED_SCRIPT_SHA256:
                raise ValueError(f"unexpected existing attention script: {destination}")
            backup = args.worktree / "originals-before-v5/attention.sh.v0.2-mixed-clock"
            stage(backup, previous)
            destination.write_bytes(data)
        else:
            stage(destination, data)
        ensure_line(config / "system_a_fs_config", f"system_a/system/{name} 0 0 {mode}")
        escaped = name.replace(".", r"\.")
        context = f"/system_a/system/{escaped} u:object_r:system_file:s0"
        ensure_line(config / "system_a_file_contexts", context)
        ensure_line(config / "system_a_file_contexts.build-ascii", context)
    print("staged ASI attention helper, listener, and native init service")


if __name__ == "__main__":
    main()
