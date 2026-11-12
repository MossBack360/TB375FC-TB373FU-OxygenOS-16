"""Package the owner-confirmed 26px SystemUI payload as the current module."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

root = Path(__file__).resolve().parents[1]
source = root / "out/systemui-drag-radius-v0.6-26px-test-2026-11-11/fixo-systemui-drag-radius-26px-v0.6-test.zip"
output = root / "out/systemui-drag-radius-v0.6-26px-confirmed-2026-11-12/fixo-systemui-drag-radius-26px-v0.6.zip"
expected_source = "f3edd480f6f202420de7d63de3737f4ad07868f4f5f85e624448758cd203b630"
expected_apk = "d5ecf22aa1c6fc3945a508c008af06554e3a1e6bcda9380258a9b266f821bf26"

assert hashlib.sha256(source.read_bytes()).hexdigest() == expected_source
with ZipFile(source) as archive:
    apk = archive.read("payload/SystemUI.apk")
    service = archive.read("service.sh")
assert hashlib.sha256(apk).hexdigest() == expected_apk

properties = (
    "id=fixo_fullscreen_caption\n"
    "name=TB375FC SystemUI fixes\n"
    "version=0.6\n"
    "versionCode=7\n"
    "author=MossBack360\n"
    "description=Fullscreen caption controls, follow-finger back animation, and 26px bottom-corner drag radius.\n"
).encode()

output.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(output, "w") as archive:
    for name, contents in {
        "module.prop": properties,
        "service.sh": service,
        "payload/SystemUI.apk": apk,
    }.items():
        entry = ZipInfo(name)
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
        archive.writestr(entry, contents)

with ZipFile(output) as archive:
    assert archive.testzip() is None
    assert archive.namelist() == ["module.prop", "service.sh", "payload/SystemUI.apk"]
    assert all("\\" not in name for name in archive.namelist())
    assert hashlib.sha256(archive.read("payload/SystemUI.apk")).hexdigest() == expected_apk
print(output)
print(hashlib.sha256(output.read_bytes()).hexdigest())
