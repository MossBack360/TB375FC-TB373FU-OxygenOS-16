from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out/oxygen-settings-fix-magisk.zip"


def add(z, source, target):
    info = zipfile.ZipInfo(target)
    info.date_time = (2020, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, source.read_bytes())


def main():
    prop = """id=oxygen_settings_fix\nname=OxygenOS Settings compatibility fix\nversion=1.0.0\nversionCode=1\nauthor=local\ndescription=Android 16 Settings multi-app API compatibility and signature bypass for OPD2203\nminMagisk=26000\n"""
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo("module.prop")
        info.date_time = (2020, 1, 1, 0, 0, 0)
        info.external_attr = 0o644 << 16
        z.writestr(info, prop)
        add(z, ROOT / "out/framework-sig-bypass.jar", "system/framework/framework.jar")
        add(z, ROOT / "out/Settings-rebuilt-signed.apk", "system/system_ext/priv-app/Settings/Settings.apk")
    print(OUT)
    print("SHA256:", hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
