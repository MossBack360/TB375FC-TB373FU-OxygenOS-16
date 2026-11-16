#!/usr/bin/env python3
"""Stage the confirmed wake-gesture and communication-sharing runtime glue."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


WAKE_SHA256 = "6509b211c93f36bf3aa785431cb70df68489d66e4550e90bd14f1d022efc0e8c"
COMM_SHA256 = "7ec62c0fc4018e8b9062077214045f7f3d51c203efa566e60ecb6748dbde3636"


def replace_once(data: bytes, old: bytes, new: bytes) -> bytes:
    if data.count(old) != 1:
        raise ValueError(f"unexpected source script: {old!r}")
    return data.replace(old, new)


def stage(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f"refusing to overwrite differing {path}")
    path.write_bytes(data)


def replace_unsafe_comm(path: Path, data: bytes, old_sha: str) -> None:
    if path.exists() and path.read_bytes() != data:
        if hashlib.sha256(path.read_bytes()).hexdigest() != old_sha:
            raise ValueError(f"unexpected communication stage: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def ensure_line(path: Path, line: str) -> None:
    if line not in path.read_text(encoding="utf-8").splitlines():
        with path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(line + "\n")


def ensure_context(path: Path, name: str) -> None:
    escaped = name.replace(".", r"\.")
    correct = f"/system_a/system/{escaped} u:object_r:system_file:s0"
    # Repair a two-backslash escape emitted by the first staging draft.
    incorrect = f"/system_a/system/{name.replace('.', chr(92) * 2 + '.')} u:object_r:system_file:s0"
    current = path.read_text(encoding="utf-8")
    if incorrect in current.splitlines():
        path.write_text(current.replace(incorrect + "\n", ""), encoding="utf-8", newline="\n")
    ensure_line(path, correct)


WAKE_RC = b"""on property:sys.boot_completed=1
    start fixo_wake_gesture

service fixo_wake_gesture /system/bin/sh /system/etc/fixo/wake-gesture.sh
    class late_start
    disabled
    user root
    group root system log input
    seclabel u:r:shell:s0
"""

COMM_RC = b"""# Disabled until the virtual radio provider initialization is understood.
service fixo_virtualcomm /system/bin/sh /system/etc/fixo/virtualcomm.sh
    class late_start
    disabled
    user root
    group root system log
    seclabel u:r:shell:s0
    oneshot
"""

COMM_DIAGNOSTIC = b"""#!/system/bin/sh
printf '%s %s\\n' \"$(date '+%F %T')\" 'virtual RIL startup deferred' > /data/local/tmp/fixo-virtualcomm.log
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wake_zip", type=Path)
    parser.add_argument("comm_zip", type=Path)
    parser.add_argument("worktree", type=Path)
    args = parser.parse_args()
    for path, expected in ((args.wake_zip, WAKE_SHA256), (args.comm_zip, COMM_SHA256)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"archive changed: {path}")
    with ZipFile(args.wake_zip) as archive:
        wake = archive.read("service.sh")
        dex = archive.read("wake-glue.dex")
    wake = replace_once(wake, b"MODDIR=${0%/*}\n", b"")
    wake = replace_once(wake, b'DEX="$MODDIR/wake-glue.dex"',
                        b'DEX="/system/etc/fixo/wake-glue.dex"')
    wake = replace_once(wake, b'LOG="$MODDIR/runtime.log"',
                        b'LOG="/data/local/tmp/fixo-wake-gesture.log"')

    with ZipFile(args.comm_zip) as archive:
        static = {
            "system/etc/sysconfig/wifi-only-tablet.xml":
                "system_a/system_a/system/etc/sysconfig/wifi-only-tablet.xml",
            "system/product/overlay/FixOVirtualCommCapabilityV2.apk":
                "product_a/product_a/overlay/FixOVirtualCommCapabilityV2.apk",
        }
        for source, dest in static.items():
            actual = args.worktree / "filesystems" / dest
            if actual.read_bytes() != archive.read(source):
                raise ValueError(f"communication static payload mismatch: {dest}")
    features = ("oplus.software.wms.panorama_work_station",
                "oplus.software.directservice.finger_flashnotes_enable",
                "oplus.software.radio.virtualmodem_wifinetwork_support",
                "oplus.software.radio.virtualmodem_support",
                "oplus.software.radio.virtualmodem_cellinfo")
    feature_table = (args.worktree / "filesystems/system_a/system_a/my_product/etc/extension/"
                     "com.oplus.oplus-feature.xml").read_text(encoding="utf-8")
    if any(feature not in feature_table for feature in features):
        raise ValueError("unified feature table is missing a communication/AI/freeform gate")
    comm = COMM_DIAGNOSTIC

    system = args.worktree / "filesystems/system_a/system_a/system"
    entries = {
        "etc/fixo/wake-gesture.sh": (wake, "0755"),
        "etc/fixo/wake-glue.dex": (dex, "0644"),
        "etc/init/fixo-wake-gesture.rc": (WAKE_RC, "0644"),
        "etc/fixo/virtualcomm.sh": (comm, "0755"),
        "etc/init/fixo-virtualcomm.rc": (COMM_RC, "0644"),
    }
    config = args.worktree / "filesystems/system_a/config"
    for name, (data, mode) in entries.items():
        if name == "etc/fixo/virtualcomm.sh":
            replace_unsafe_comm(system / name, data,
                                "034d47d76417f92f1ef7458d33df5264c93c91f6c65956323d09de766ffd7a58")
        elif name == "etc/init/fixo-virtualcomm.rc":
            replace_unsafe_comm(system / name, data,
                                "bb0647221a4f6811c000da22526e8ca406c634655e9c42d82698c11e4e83210d")
        else:
            stage(system / name, data)
        ensure_line(config / "system_a_fs_config", f"system_a/system/{name} 0 0 {mode}")
        ensure_context(config / "system_a_file_contexts", name)
        ensure_context(config / "system_a_file_contexts.build-ascii", name)

    # Remove the old signal grant: the unverified subsystem restart is disabled.
    cil = args.worktree / "filesystems/system_ext_a/system_ext_a/etc/selinux/system_ext_sepolicy.cil"
    lines = cil.read_text(encoding="utf-8").splitlines()
    stale = {"; FixO communication-sharing cached subsystem restart",
             "(allow shell system_app (process (sigkill)))"}
    if stale.intersection(lines):
        cil.write_text("\n".join(line for line in lines if line not in stale) + "\n",
                       encoding="utf-8", newline="\n")
    print("staged wake service; disabled unsafe virtual RIL startup")


if __name__ == "__main__":
    main()
