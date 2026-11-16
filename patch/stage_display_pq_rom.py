#!/usr/bin/env python3
"""Stage the tested PQ bridge and its narrow MTK HAL policy in the v5 ROM tree."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


MODULE_SHA256 = "bcc051e9c6ffa151cb07edced3920645c3386b4d306f9fb8829907981d652659"
BASE_CIL_SHA256 = "ae9ce3a2a9ce4efddcd6c7c4807dd1c8d7c3dc557d39e42b815591029236afe4"
POLICY = (
    b"\n; FixO PQ shell bridge\n"
    b"(allow shell mtk_hal_pq_hwservice (hwservice_manager (find)))\n"
    b"(allow shell mtk_hal_pq (binder (call)))\n"
)
RC = b"""on property:sys.boot_completed=1
    start fixo_display_pq

service fixo_display_pq /system/bin/sh /system/etc/fixo/display-pq.sh
    class late_start
    disabled
    user root
    group root system log
    seclabel u:r:shell:s0
"""


def ensure_line(path: Path, line: str) -> None:
    data = path.read_text(encoding="utf-8")
    if line not in data.splitlines():
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line + "\n")


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
    if hashlib.sha256(args.module_zip.read_bytes()).hexdigest() != MODULE_SHA256:
        raise ValueError("PQ v1.1 module changed")
    with ZipFile(args.module_zip) as archive:
        script = archive.read("service.sh")
        jar = archive.read("pqctl.jar")
    if b'if [ "$result" = true ]; then' not in script:
        raise ValueError("PQ result check missing")
    original = b'CTL="$MODDIR/pqctl.jar"'
    if script.count(original) != 1:
        raise ValueError("unexpected PQ controller path")
    script = script.replace(original, b'CTL="/system/etc/fixo/pqctl.jar"')

    base = args.worktree / "filesystems"
    system = base / "system_a/system_a/system"
    stage(system / "etc/fixo/display-pq.sh", script)
    stage(system / "etc/fixo/pqctl.jar", jar)
    stage(system / "etc/init/fixo-display-pq.rc", RC)
    config = base / "system_a/config"
    for name, mode in (("etc/fixo/display-pq.sh", "0755"),
                       ("etc/fixo/pqctl.jar", "0644"),
                       ("etc/init/fixo-display-pq.rc", "0644")):
        ensure_line(config / "system_a_fs_config", f"system_a/system/{name} 0 0 {mode}")
        escaped = name.replace(".", r"\.")
        line = f"/system_a/system/{escaped} u:object_r:system_file:s0"
        ensure_line(config / "system_a_file_contexts", line)
        ensure_line(config / "system_a_file_contexts.build-ascii", line)

    cil = base / "system_ext_a/system_ext_a/etc/selinux/system_ext_sepolicy.cil"
    current = cil.read_bytes()
    if current.endswith(POLICY):
        pass
    elif hashlib.sha256(current).hexdigest() == BASE_CIL_SHA256:
        cil.write_bytes(current + POLICY)
    else:
        raise ValueError("system_ext policy changed unexpectedly")
    print("staged PQ controller, init service, and two SELinux permissions")


if __name__ == "__main__":
    main()
