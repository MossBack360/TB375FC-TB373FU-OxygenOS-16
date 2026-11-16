"""Route the hidden AOSP lift switch to the working global sensor bridge."""

import hashlib
import struct
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "out/settings-signature-audit-2026-11-12/Settings-v5.3-rom-signing-block-candidate.apk"
APKTOOL = ROOT / "tools/apktool_3.0.3.jar"
OUT = ROOT / "out/wake-switch-2026-11-16"
SOURCE_SHA = "4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098"
CLASS = OUT / "decoded/smali/com/android/settings/display/LiftToWakePreferenceController.smali"
MAGIC = b"APK Sig Block 42"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cd_offset(data):
    end = data.rfind(b"PK\x05\x06")
    assert end >= 0 and end + 22 + struct.unpack_from("<H", data, end + 20)[0] == len(data)
    offset = struct.unpack_from("<I", data, end + 16)[0]
    assert data[offset:offset + 4] == b"PK\x01\x02"
    return offset, end


def main():
    original = SOURCE.read_bytes()
    assert sha(original) == SOURCE_SHA
    OUT.mkdir(parents=True, exist_ok=True)
    mini = OUT / "Settings-classes5-only.apk"
    with ZipFile(SOURCE) as src, ZipFile(mini, "w") as dst:
        dst.writestr("AndroidManifest.xml", src.read("AndroidManifest.xml"))
        dst.writestr("classes.dex", src.read("classes5.dex"))

    decoded = OUT / "decoded"
    if not decoded.exists():
        subprocess.run(["java", "-jar", str(APKTOOL), "d", "-r", "-f", str(mini), "-o", str(decoded)], check=True)
    smali = CLASS.read_text(encoding="utf-8")
    old_key = "wake_gesture_enabled"
    old_api = "Landroid/provider/Settings$Secure;"
    new_key = "ambient_tilt_to_wake"
    new_api = "Landroid/provider/Settings$Global;"
    if smali.count(old_key) == 2 and smali.count(old_api) == 2:
        CLASS.write_text(smali.replace(old_key, new_key).replace(old_api, new_api), encoding="utf-8")
    else:
        assert smali.count(new_key) == 2 and smali.count(new_api) == 2

    built = OUT / "Settings-classes5-patched.apk"
    subprocess.run(["java", "-jar", str(APKTOOL), "b", str(decoded), "-o", str(built)], check=True)
    with ZipFile(built) as package:
        dex = package.read("classes.dex")
    assert new_key.encode() in dex

    unsigned = OUT / "Settings-v5.4-unsigned.apk"
    with ZipFile(SOURCE) as src, ZipFile(unsigned, "w") as dst:
        for entry in src.infolist():
            dst.writestr(entry, dex if entry.filename == "classes5.dex" else src.read(entry.filename))
    with ZipFile(SOURCE) as src, ZipFile(unsigned) as dst:
        assert src.namelist() == dst.namelist()
        assert [name for name in src.namelist() if src.read(name) != dst.read(name)] == ["classes5.dex"]

    cd, _ = cd_offset(original)
    assert original[cd - 16:cd] == MAGIC
    size = struct.unpack_from("<Q", original, cd - 24)[0]
    start = cd - size - 8
    assert struct.unpack_from("<Q", original, start)[0] == size
    block = original[start:cd]
    data = unsigned.read_bytes()
    target_cd, target_end = cd_offset(data)
    candidate = bytearray(data[:target_cd] + block + data[target_cd:])
    struct.pack_into("<I", candidate, target_end + len(block) + 16, target_cd + len(block))
    apk = OUT / "Settings-v5.4-rom-signing-block-candidate.apk"
    apk.write_bytes(candidate)
    assert cd_offset(candidate)[0] == target_cd + len(block)

    prop = b"id=fixo_settings_rom_scan_trial\nname=Settings ROM scan trial\nversion=0.2-lift-switch\nversionCode=2\nauthor=MossBack360\ndescription=Settings v5.3 plus hidden lift-switch linkage to ambient_tilt_to_wake.\n"
    module = OUT / "fixo-settings-lift-switch-v0.2.zip"
    with ZipFile(module, "w") as archive:
        for name, payload in {"module.prop": prop, "system/system_ext/priv-app/Settings/Settings.apk": bytes(candidate)}.items():
            entry = ZipInfo(name)
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, payload)
    with ZipFile(module) as archive:
        assert archive.testzip() is None
        assert all("\\" not in name for name in archive.namelist())
    print("APK", apk, sha(candidate))
    print("ZIP", module, sha(module.read_bytes()))


if __name__ == "__main__":
    main()
