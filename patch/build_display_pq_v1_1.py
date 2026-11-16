#!/usr/bin/env python3
"""Build the PQ v1.1 trial without changing the confirmed v1.0 archive."""

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "temp3/稳定安装/01-当前启用-Magisk/09-display-pq-config-bridge-v1.0.zip"
OUT = ROOT / "out/display-pq-bridge-v1.1-2026-11-16/fixo-display-pq-v1.1-magisk.zip"
EXPECTED_SHA256 = "2f1e4f910654b56de6545bff8aa6130956b887983f6cd75316d045541aa5e41f"

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_SHA256:
    raise ValueError("confirmed v1.0 archive changed")
with ZipFile(SOURCE) as archive:
    jar = archive.read("pqctl.jar")
    metadata = archive.read("module.prop").decode()
script = (ROOT / "patch/display-pq-controller/service-v1.1.sh").read_bytes()
if b'if [ "$result" = true ]; then' not in script:
    raise ValueError("controller result check missing")
metadata = metadata.replace("version=1.0\n", "version=1.1\n")
metadata = metadata.replace("versionCode=1\n", "versionCode=2\n")
if "version=1.1\n" not in metadata or "versionCode=2\n" not in metadata:
    raise ValueError("version change failed")

OUT.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(OUT, "w") as archive:
    for name, data, mode in (
        ("module.prop", metadata.encode(), 0o100644),
        ("service.sh", script, 0o100755),
        ("pqctl.jar", jar, 0o100644),
    ):
        entry = ZipInfo(name)
        entry.create_system = 3
        entry.compress_type = ZIP_DEFLATED
        entry.external_attr = mode << 16
        archive.writestr(entry, data)
with ZipFile(OUT) as archive:
    if archive.testzip() is not None or any("\\" in name for name in archive.namelist()):
        raise ValueError("invalid ZIP")
    if archive.read("pqctl.jar") != jar:
        raise ValueError("controller JAR changed")
print(OUT)
print(hashlib.sha256(OUT.read_bytes()).hexdigest())
