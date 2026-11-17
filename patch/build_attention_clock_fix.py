#!/usr/bin/env python3
"""Package the screen-attention clock fix over the preserved v0.2 module."""

import hashlib
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "out/attention-asi-glue-v0.2-2026-09-14/fixo-attention-asi-v0.2-trial-magisk.zip"
BASE_SHA256 = "c05e9acc429e691d737eae054354dbb8ee7a9fb20fd54f4b0605946d2187613e"
SOURCE = ROOT / "patch/modules/fixo_attention_asi"
OUTPUT = ROOT / "out/attention-asi-clock-fix-v0.3-2026-11-17/fixo-attention-asi-v0.3-clock-fix.zip"


def main() -> None:
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA256:
        raise ValueError("unexpected v0.2 base module")
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(BASE) as original, ZipFile(OUTPUT, "w") as target:
        for info in original.infolist():
            if "\\" in info.filename:
                raise ValueError(f"invalid ZIP path: {info.filename}")
            source_file = SOURCE / info.filename
            data = source_file.read_bytes() if source_file.is_file() else original.read(info.filename)
            target.writestr(info, data)
    with ZipFile(OUTPUT) as verify:
        names = verify.namelist()
        if names != ["attention-useractivity.apk", "customize.sh", "module.prop", "README.md", "service.sh", "uninstall.sh"]:
            raise ValueError(names)
        if any("\\" in name for name in names):
            raise ValueError("backslash in ZIP path")
        if hashlib.sha256(verify.read("attention-useractivity.apk")).hexdigest() != "755a62d642204de06737a28325825634b25f4eb66f55f83b418d5bd9f32217fa":
            raise ValueError("helper changed")
        if b"versionCode=3" not in verify.read("module.prop"):
            raise ValueError("module version unchanged")
    print(f"{OUTPUT}\nsha256={hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
