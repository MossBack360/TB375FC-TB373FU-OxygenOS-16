"""Build a reversible early-mount test of the retained-signing-block Settings APK."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
APK = ROOT / "out/settings-signature-audit-2026-11-12/Settings-v5.3-rom-signing-block-candidate.apk"
OUT = ROOT / "out/settings-rom-scan-trial-2026-11-12/fixo-settings-rom-scan-trial-v0.1.zip"
EXPECTED = "4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098"
assert hashlib.sha256(APK.read_bytes()).hexdigest() == EXPECTED

properties = (
    "id=fixo_settings_rom_scan_trial\n"
    "name=Settings ROM scan trial\n"
    "version=0.1-test\n"
    "versionCode=1\n"
    "author=MossBack360\n"
    "description=Early-mount test of Settings v5.3 with retained ROM signing block.\n"
).encode()

OUT.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(OUT, "w") as archive:
    for name, data in {
        "module.prop": properties,
        "system/system_ext/priv-app/Settings/Settings.apk": APK.read_bytes(),
    }.items():
        entry = ZipInfo(name)
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = 0o100644 << 16
        archive.writestr(entry, data)

with ZipFile(OUT) as archive:
    assert archive.testzip() is None
    assert all("\\" not in name for name in archive.namelist())
    assert hashlib.sha256(archive.read("system/system_ext/priv-app/Settings/Settings.apk")).hexdigest() == EXPECTED
print(OUT)
print(hashlib.sha256(OUT.read_bytes()).hexdigest())
