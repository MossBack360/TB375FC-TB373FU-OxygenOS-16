"""Package the stock ZUI privacy APK as a Magisk module."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "build/zui-lenovo-privacy-module"
OUT = ROOT / "out/zui-camera-privacy-test-2026-09-08/fixo-zui-camera-privacy-v1.2-magisk.zip"


def main() -> None:
    entries = {
        "module.prop": SRC / "module.prop",
        "system/priv-app/ZuiLenovoPrivacy/ZuiLenovoPrivacy.apk":
            SRC / "system/system/priv-app/ZuiLenovoPrivacy/ZuiLenovoPrivacy.apk",
    }
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, source in entries.items():
            archive.write(source, name)
    with zipfile.ZipFile(OUT) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == list(entries)
        assert all("\\" not in name for name in archive.namelist())
    print(OUT)


if __name__ == "__main__":
    main()
