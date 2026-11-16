"""Restore the confirmed Settings payload without duplicate performance glue."""

import hashlib
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "temp3/稳定安装/01-当前启用-Magisk/20-settings-apk-fix-v5.3-original-sound-effects.zip"
OUT = ROOT / "out/settings-postboot-recovery-2026-11-16/fixo-settings-postboot-v5.3-recovery.zip"


def main():
    with ZipFile(SOURCE) as src:
        apk = src.read("payload/Settings.apk")
        service = src.read("service.sh")
    line = b'    sh "$MODDIR/high_performance_bridge.sh" >>"$MODDIR/high_performance_bridge.log" 2>&1 &\n'
    assert service.count(line) == 1
    service = service.replace(line, b"")
    prop = ("id=fixo_settings_confirmed\nname=Settings APK Fix\n"
            "version=5.3-postboot-recovery\nversionCode=26\nauthor=MossBack360\n"
            "description=Confirmed v5.3 Settings payload; power bridge remains in companion module.\n").encode()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w") as dst:
        for name, data in {"module.prop": prop, "service.sh": service,
                           "payload/Settings.apk": apk}.items():
            item = ZipInfo(name)
            item.compress_type = ZIP_DEFLATED
            item.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            dst.writestr(item, data)
    with ZipFile(OUT) as dst:
        assert dst.testzip() is None
        assert all("\\" not in name for name in dst.namelist())
        assert dst.read("payload/Settings.apk") == apk
    print(OUT)
    print(hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
