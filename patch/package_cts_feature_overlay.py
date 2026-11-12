"""Upgrade the existing CTS feature module with a framework provider overlay."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(r"E:\工程\github\xiaoxin Oxygen\temp3\稳定安装\01-当前启用-Magisk\22-circle-to-search-feature-config-v0.2-test.zip")
OVERLAY = ROOT / "out/cts-native-v0.1-2026-11-12/cts-framework-overlay-signed.apk"
OUTPUT = ROOT / "out/cts-native-v0.1-2026-11-12/fixo-circle-to-search-framework-v0.3-test.zip"


def main() -> None:
    assert hashlib.sha256(BASE.read_bytes()).hexdigest() == "916256fb2d63eca63de85b3f80cae95a763410581ec43007e8d724980aafa4f9"
    with ZipFile(BASE) as archive:
        feature = archive.read("system/etc/permissions/fixo_circle_to_search.xml")
    overlay = OVERLAY.read_bytes()
    assert overlay.startswith(b"PK")
    prop = (
        "id=fixo_circle_to_search\n"
        "name=FixO Circle to Search framework trial\n"
        "version=0.3-test\nversionCode=3\nauthor=MossBack360\n"
        "description=Declare Contextual Search and select Google as framework provider.\n"
    ).encode()
    files = {
        "module.prop": prop,
        "system/etc/permissions/fixo_circle_to_search.xml": feature,
        "system/product/overlay/FixOCtsFramework.apk": overlay,
    }
    with ZipFile(OUTPUT, "w") as archive:
        for name, data in files.items():
            entry = ZipInfo(name)
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    with ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == list(files)
        assert all("\\" not in name for name in archive.namelist())
    print(OUTPUT, hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
