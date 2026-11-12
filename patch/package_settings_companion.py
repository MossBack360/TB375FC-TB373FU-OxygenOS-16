"""Split the v5.3 Settings properties and power bridge from its APK payload."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "temp3/稳定安装/01-当前启用-Magisk/20-settings-apk-fix-v5.3-original-sound-effects.zip"
OUT = ROOT / "out/settings-companion-v0.1-2026-11-12/fixo-settings-companion-v0.1.zip"
EXPECTED = "24699e6a9b12c4d74d6d858b123a2c71665fb24132344e24c04ca05d82e74f4c"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED

with ZipFile(SOURCE) as original:
    props = original.read("system.prop")
    bridge = original.read("high_performance_bridge.sh")
assert props == b"persist.sys.oplus.nandswap.storage.min=19\nro.build.release_type=true\n"
assert b"settings get system high_performance_mode_on" in bridge
assert b"cmd power set-fixed-performance-mode-enabled" in bridge

metadata = (
    "id=fixo_settings_companion\n"
    "name=Settings companion configuration\n"
    "version=0.1\n"
    "versionCode=1\n"
    "author=MossBack360\n"
    "description=Settings-related properties and the high-performance PowerManager bridge.\n"
).encode()
service = (
    b"#!/system/bin/sh\n"
    b"MODDIR=${0%/*}\n"
    b"sh \"$MODDIR/high_performance_bridge.sh\" >>\"$MODDIR/high_performance_bridge.log\" 2>&1 &\n"
)

OUT.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(OUT, "w") as archive:
    for name, data in {
        "module.prop": metadata,
        "system.prop": props,
        "service.sh": service,
        "high_performance_bridge.sh": bridge,
    }.items():
        entry = ZipInfo(name)
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
        archive.writestr(entry, data)

with ZipFile(OUT) as archive:
    assert archive.testzip() is None
    assert all("\\" not in name for name in archive.namelist())
    assert archive.read("system.prop") == props
    assert archive.read("high_performance_bridge.sh") == bridge
print(OUT)
print(hashlib.sha256(OUT.read_bytes()).hexdigest())
