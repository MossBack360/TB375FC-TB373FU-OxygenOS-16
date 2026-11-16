"""Package the lift-switch-only Settings DEX change for post-scan binding."""

import hashlib
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "out/settings-postboot-recovery-2026-11-16/fixo-settings-postboot-v5.3-recovery.zip"
APK = ROOT / "out/wake-switch-2026-11-16/Settings-v5.4-unsigned.apk"
OUT = ROOT / "out/wake-switch-2026-11-16/fixo-settings-lift-switch-v5.4-postboot.zip"
EXPECTED = "393119a3cd00231a207232f94a0d187875ccf552ce07b998f929520c83cdf3b2"


def main():
    assert hashlib.sha256(BASE.read_bytes()).hexdigest() == EXPECTED
    with ZipFile(BASE) as source:
        original = source.read("payload/Settings.apk")
        service = source.read("service.sh")
    candidate = APK.read_bytes()
    with ZipFile(APK) as patched, ZipFile(Path(ROOT / "out/settings-signature-audit-2026-11-12/Settings-patched-v5.3.apk")) as old:
        assert patched.namelist() == old.namelist()
        assert [n for n in old.namelist() if old.read(n) != patched.read(n)] == ["classes5.dex"]
    assert original != candidate
    prop = ("id=fixo_settings_confirmed\nname=Settings APK Fix\n"
            "version=5.4-lift-switch\nversionCode=27\nauthor=MossBack360\n"
            "description=Confirmed Settings v5.3 plus AOSP lift switch linked to ambient_tilt_to_wake.\n").encode()
    with ZipFile(OUT, "w") as archive:
        for name, data in {"module.prop": prop, "service.sh": service,
                           "payload/Settings.apk": candidate}.items():
            entry = ZipInfo(name)
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            archive.writestr(entry, data)
    with ZipFile(OUT) as archive:
        assert archive.testzip() is None
        assert all("\\" not in name for name in archive.namelist())
    print(OUT, hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
