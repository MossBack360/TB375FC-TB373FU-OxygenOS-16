#!/usr/bin/env python3
"""Stage confirmed AI and ZUI writeback glue in the unpacked v5 system tree."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


AI_SHA256 = "989a6f3e7ba461a9ab60e183a4b0783c38fc3b3b8caa318ffe86ef319b833509"
ZRAM_SHA256 = "6d4bfa8ddac9ba7ed1b0b73474bff01185aea038977b7bf7050902179cca6735"
ZRAM_LINE = "/dev/block/zram0 none swap defaults zramsize=100%,zram_backingdev_size={}\n"
ZRAM_SIZES = (2, 4, 6, 8, 12, 16)


def replace_once(data: bytes, old: bytes, new: bytes) -> bytes:
    if data.count(old) != 1:
        raise ValueError(f"expected one occurrence of {old!r}")
    return data.replace(old, new)


def stage(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f"refusing to overwrite differing {path}")
    path.write_bytes(data)


def ensure_line(path: Path, line: str) -> None:
    current = path.read_text(encoding="utf-8")
    if line not in current.splitlines():
        with path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(line + "\n")


def mount_lines(size: str) -> list[str]:
    source = f"/system/etc/fixo/zram/fstab.{size}"
    return [f"    mount none {source} /vendor/etc/{name} bind"
            for name in ("fstab.enableswap", "fstab.zram_wb")]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ai_zip", type=Path)
    parser.add_argument("zram_zip", type=Path)
    parser.add_argument("worktree", type=Path)
    args = parser.parse_args()
    for archive, expected in ((args.ai_zip, AI_SHA256), (args.zram_zip, ZRAM_SHA256)):
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise ValueError(f"archive changed: {archive}")
    with ZipFile(args.ai_zip) as archive:
        ai = archive.read("service.sh")
    ai = replace_once(ai, b"MODDIR=${0%/*}\n", b"")
    ai = replace_once(ai, b'LOG="$MODDIR/runtime.log"',
                      b'LOG="/data/local/tmp/fixo-ai-providers.log"')
    ai = replace_once(ai, b'su -Z u:r:shell:s0 2000 -c "settings $*" 2>/dev/null',
                      b'settings "$@" 2>/dev/null')
    if b"su -Z" in ai or b"$MODDIR" in ai:
        raise ValueError("AI Magisk dependency remains")

    with ZipFile(args.zram_zip) as archive:
        zram = archive.read("service.sh")
    zram = replace_once(zram, b"moddir=${0%/*}\n", b"")
    zram = replace_once(zram, b'logfile="$moddir/runtime.log"',
                        b'logfile="/data/local/tmp/fixo-zram-writeback.log"')
    if b"$moddir" in zram:
        raise ValueError("ZRAM Magisk dependency remains")

    system = args.worktree / "filesystems/system_a/system_a/system"
    entries = {
        "etc/fixo/ai-providers.sh": (ai, "0755"),
        "etc/fixo/zram-writeback.sh": (zram, "0755"),
    }
    ai_rc = b"""on property:sys.boot_completed=1
    start fixo_ai_providers

service fixo_ai_providers /system/bin/sh /system/etc/fixo/ai-providers.sh
    class late_start
    disabled
    user shell
    group shell system log
    seclabel u:r:shell:s0
"""
    entries["etc/init/fixo-ai-providers.rc"] = (ai_rc, "0644")

    # ZUI calls swapon_all only after boot_completed; this event runs after
    # init has loaded persistent Settings properties, before that swapon_all.
    lines = ["# Select ZUI's UFS backing size before either vendor swapon_all call."]
    for enabled, size, source in [("false", None, "0"),
                                  *(("true", n, f"{n}G") for n in ZRAM_SIZES)]:
        trigger = f"on load_persist_props_action && property:persist.sys.oplus.nandswap={enabled}"
        if size is not None:
            trigger += f" && property:persist.sys.oplus.nandswap.swapsize={size}"
        lines.extend((trigger, *mount_lines(source), ""))
    lines.extend((
        "on property:sys.boot_completed=1",
        "    start fixo_zram_writeback",
        "",
        "service fixo_zram_writeback /system/bin/sh /system/etc/fixo/zram-writeback.sh",
        "    class late_start",
        "    disabled",
        "    user root",
        "    group root system log",
        "    seclabel u:r:shell:s0",
        "",
    ))
    entries["etc/init/fixo-zram-writeback.rc"] = ("\n".join(lines).encode(), "0644")
    for size in ("0", *(f"{n}G" for n in ZRAM_SIZES)):
        entries[f"etc/fixo/zram/fstab.{size}"] = (ZRAM_LINE.format(size).encode(), "0644")

    cfg = args.worktree / "filesystems/system_a/config"
    for name, (data, mode) in entries.items():
        stage(system / name, data)
        ensure_line(cfg / "system_a_fs_config", f"system_a/system/{name} 0 0 {mode}")
        pattern = name.replace(".", r"\.")
        context = f"/system_a/system/{pattern} u:object_r:system_file:s0"
        ensure_line(cfg / "system_a_file_contexts", context)
        ensure_line(cfg / "system_a_file_contexts.build-ascii", context)
    ensure_line(cfg / "system_a_fs_config", "system_a/system/etc/fixo/zram 0 0 0755")

    # The existing ROM has no write permission for shell on sysfs_zram.
    # Limit the new permission to that sysfs type; keep all other policy intact.
    cil = args.worktree / "filesystems/system_ext_a/system_ext_a/etc/selinux/system_ext_sepolicy.cil"
    rule = "(allow shell sysfs_zram (file (getattr open read write)))"
    old_rule = "(allow shell sysfs_zram (file (open write)))"
    current = cil.read_text(encoding="utf-8")
    if old_rule in current:
        cil.write_text(current.replace(old_rule, rule), encoding="utf-8", newline="\n")
    else:
        ensure_line(cil, "; FixO ZUI writeback shell bridge")
        ensure_line(cil, rule)
    print(f"staged {len(entries)} AI/ZRAM files, two init services, and one SELinux rule")


if __name__ == "__main__":
    main()
