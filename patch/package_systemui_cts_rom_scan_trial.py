"""Reversible early-mount SystemUI CTS test under the existing module ID."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
APK = ROOT / "out/cts-native-v0.1-2026-11-12/SystemUI-cts-rom-scan-candidate.apk"
OUTPUT = ROOT / "out/cts-native-v0.1-2026-11-12/fixo-systemui-cts-rom-scan-v0.8-test.zip"
EXPECTED = "a4aa5664013ada9a87089a142b7d6f4a2328d62b2c5ddd22f16213dea7d339b1"


def main() -> None:
    data = APK.read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED
    props = (
        "id=fixo_fullscreen_caption\n"
        "name=TB375FC SystemUI fixes and native Circle to Search\n"
        "version=0.8-cts-rom-scan-test\nversionCode=9\nauthor=MossBack360\n"
        "description=Early-mount test of confirmed SystemUI fixes plus native Home-bar CTS dispatch.\n"
    ).encode()
    files = {
        "module.prop": props,
        "system/system_ext/priv-app/SystemUI/SystemUI.apk": data,
    }
    with ZipFile(OUTPUT, "w") as archive:
        for name, contents in files.items():
            entry = ZipInfo(name)
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, contents)
    with ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == list(files)
        assert all("\\" not in n for n in archive.namelist())
    print(OUTPUT, hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
