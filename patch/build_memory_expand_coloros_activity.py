"""Port the one proven TB375FC ColorOS RAM-expansion activity difference."""

from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import struct
import subprocess
import zipfile
from pathlib import Path


EXPECTED_BASE = "76b66e842a6b19a7824bd5abe608d74b2bccf0d875b46515642625f8f3998ffe"
EXPECTED_BOOT_SCAN_APK = "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"
EXPECTED_CURRENT_CLASS = "dd41ffcbe66a32ebf2685e727b5fb263b8eb2f0dfee917110ea47c85452f65ff"
EXPECTED_COLOROS_CLASS = "e8d55b06357afdd10cc95a8685362a8757d5bcaa5590410787abb5dc7f26eaed"
CLASS = Path("smali_classes2/com/oplus/settings/feature/ramexpand/RamExpandSizePreference.smali")
SAME_CLASSES = (
    "RamExpandFragment.smali",
    "RamExpandSwitchPreferenceController.smali",
    "RamExpandUtils.smali",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aligned_apk(base_path: Path, dex_path: Path, output: Path) -> None:
    with zipfile.ZipFile(base_path) as base, zipfile.ZipFile(output, "w") as result:
        for entry in base.infolist():
            info = copy.copy(entry)
            info.extra = b""
            if info.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if info.filename.startswith("lib/") and info.filename.endswith(".so") else 4
                offset = result.fp.tell() + 30 + len(info.filename.encode("utf-8"))
                if offset % alignment:
                    padding = (-offset - 4) % alignment
                    info.extra = struct.pack("<HH", 0xFFFF, padding) + bytes(padding)
            result.writestr(info, dex_path.read_bytes() if entry.filename == "classes2.dex" else base.read(entry))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    stage = (args.stage or root).resolve()

    base = root / "out/settings-easter-logo-only-2026-09-08/Settings-easter-oxygen-logo.apk"
    module_base = root / "out/settings-easter-logo-only-2026-09-08/fixo-settings-easter-logo-only-magisk.zip"
    apktool = root / "tools/apktool_3.0.3.jar"
    donor_root = root / "work/xiaoxin-color/smali_classes2/com/oplus/settings/feature/ramexpand"
    current_root = root / "work/current/smali_classes2/com/oplus/settings/feature/ramexpand"
    assert digest(base) == EXPECTED_BASE
    assert digest(current_root / CLASS.name) == EXPECTED_CURRENT_CLASS
    assert digest(donor_root / CLASS.name) == EXPECTED_COLOROS_CLASS
    for name in SAME_CLASSES:
        assert (current_root / name).read_bytes() == (donor_root / name).read_bytes(), name

    work = stage / "work/memory-expand-coloros-activity"
    dest = stage / "out/memory-expand-coloros-activity-2026-09-12"
    assert not work.exists() and not dest.exists(), "Refusing to overwrite an earlier build"
    work.parent.mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True)
    subprocess.run(["java", "-Xmx3g", "-jar", str(apktool), "d", "-r", str(base), "-o", str(work)], check=True)

    target = work / CLASS
    before = target.read_text(encoding="utf-8")
    assert hashlib.sha256(target.read_bytes()).hexdigest() == EXPECTED_CURRENT_CLASS
    after = (donor_root / CLASS.name).read_text(encoding="utf-8")
    target.write_text(after, encoding="utf-8", newline="\n")
    patch = dest / "coloros-activity-exact.patch"
    patch.write_text(
        "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), str(CLASS), str(CLASS))),
        encoding="utf-8",
        newline="\n",
    )
    subprocess.run(["java", "-Xmx3g", "-jar", str(apktool), "b", "-j", "8", "--no-apk", str(work)], check=True)

    apk = dest / "Settings-memory-expand-coloros-activity.apk"
    aligned_apk(base, work / "build/apk/classes2.dex", apk)
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(apk) as new:
        assert new.testzip() is None
        assert new.namelist() == old.namelist()
        assert [name for name in old.namelist() if old.read(name) != new.read(name)] == ["classes2.dex"]

    module = dest / "fixo-settings-memory-expand-coloros-activity-v3.9-magisk.zip"
    module_prop = (
        "id=fixo_settings_confirmed\n"
        "name=Settings - OxygenOS UI and ColorOS RAM activity\n"
        "version=3.9\n"
        "versionCode=12\n"
        "author=local\n"
        "description=Confirmed Settings UI with the exact TB375FC ColorOS RAM-expansion activity writeback.\n"
    ).encode()
    with zipfile.ZipFile(module_base) as old, zipfile.ZipFile(module, "w") as new:
        for entry in old.infolist():
            data = old.read(entry)
            if entry.filename == "payload/Settings.apk":
                data = apk.read_bytes()
            elif entry.filename == "module.prop":
                data = module_prop
            new.writestr(entry, data)
        new.writestr("system.prop", b"persist.sys.oplus.nandswap.storage.min=19\n")
    with zipfile.ZipFile(module) as built, zipfile.ZipFile(module_base) as stable:
        assert built.testzip() is None
        assert built.read("payload/Settings.apk") == apk.read_bytes()
        assert built.read("system.prop") == b"persist.sys.oplus.nandswap.storage.min=19\n"
        scan = built.read("system/system_ext/priv-app/Settings/Settings.apk")
        assert hashlib.sha256(scan).hexdigest() == EXPECTED_BOOT_SCAN_APK
        assert scan == stable.read("system/system_ext/priv-app/Settings/Settings.apk")

    outputs = (apk, module, patch)
    (dest / "SHA256SUMS.txt").write_text(
        "".join(f"{digest(path)}  {path.name}\n" for path in outputs), encoding="ascii"
    )
    print((dest / "SHA256SUMS.txt").read_text(encoding="ascii"), end="")
    print("PASS: exact ColorOS activity class used; original APK retained for PackageManager boot scan")


if __name__ == "__main__":
    main()
