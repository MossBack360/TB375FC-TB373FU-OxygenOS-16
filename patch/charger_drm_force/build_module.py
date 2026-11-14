#!/usr/bin/env python3
"""Build a reversible off-mode DRM blank trial from verified binaries."""

from pathlib import Path
import hashlib
import sys
import zipfile

CHARGER_SHA256 = "ca444a23efa4e760d23506df4e09c5249df05a9c265e9928f6844338cfae12b5"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    charger, helper, output = map(Path, sys.argv[1:4])
    if sha256(charger.read_bytes()) != CHARGER_SHA256:
        raise ValueError("Unexpected charger binary")
    if not helper.read_bytes().startswith(b"\x7fELF"):
        raise ValueError("Helper is not ELF")
    script = Path(__file__).with_name("post-fs-data.sh").read_bytes().replace(b"\r\n", b"\n")
    prop = b"\n".join([
        b"id=fixo_charger_verbose_trial",
        b"name=TB375FC Charger DRM Blank Wake Trial",
        b"version=0.4-drm-paired-test",
        b"versionCode=4",
        b"author=MossBack360",
        b"description=Pair DSI CRTC blank and wake in off-mode charging.",
        b"",
    ])
    installer = b"#!/system/bin/sh\nset_perm $MODPATH/system/bin/charger 0 0 0755\nset_perm $MODPATH/system/bin/charger_drm_blank 0 0 0755\nset_perm $MODPATH/post-fs-data.sh 0 0 0755\n"
    entries = {
        "module.prop": (prop, 0o644),
        "customize.sh": (installer, 0o755),
        "post-fs-data.sh": (script, 0o755),
        "system/bin/charger": (charger.read_bytes(), 0o755),
        "system/bin/charger_drm_blank": (helper.read_bytes(), 0o755),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, (data, mode) in entries.items():
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (mode | 0o100000) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == set(entries)
        assert all("\\" not in name for name in archive.namelist())
        assert all(archive.read(name) == entries[name][0] for name in entries)
    print(f"zip={output}")
    print(f"helper_sha256={sha256(helper.read_bytes())}")


if __name__ == "__main__":
    main()
