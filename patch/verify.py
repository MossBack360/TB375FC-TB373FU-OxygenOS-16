"""Offline integrity/API checks; does not replace testing on the target ROM."""
from pathlib import Path
import hashlib
import struct
import zipfile
import zlib

from apply_patch import ROOT, BASE, FILES, OLD, NEW
from package_apk import SIGNATURES


def main():
    source = ROOT / "extract/Settings.apk"
    output = ROOT / "out/Settings-fixed-unsigned.apk"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output) as patched, output.open("rb") as raw:
        assert patched.testzip() is None
        assert set(patched.namelist()) == set(original.namelist()) - SIGNATURES
        changed = [n for n in patched.namelist() if patched.read(n) != original.read(n)]
        assert changed == ["classes2.dex"], changed
        for info in patched.infolist():
            if info.compress_type == zipfile.ZIP_STORED:
                raw.seek(info.header_offset + 26)
                name_len, extra_len = struct.unpack("<HH", raw.read(4))
                offset = info.header_offset + 30 + name_len + extra_len
                alignment = 16384 if info.filename.startswith("lib/") and info.filename.endswith(".so") else 4
                assert offset % alignment == 0, info.filename
            if info.filename.endswith(".dex"):
                data = patched.read(info)
                assert data[:4] == b"dex\n"
                assert struct.unpack_from("<I", data, 32)[0] == len(data)
                assert data[12:32] == hashlib.sha1(data[32:]).digest()
                assert struct.unpack_from("<I", data, 8)[0] == zlib.adler32(data[12:])

    # Check the assembled DEX after an independent apktool disassembly.
    decoded = ROOT / "work/verify/smali/com/oplus/settings"
    for name in FILES:
        text = (decoded / name).read_text(encoding="utf-8")
        assert OLD not in text, name
        assert text.count(NEW) == 1, name
        assert any("invoke-static" in line and NEW in line for line in text.splitlines()), name

    dependencies = {
        "work/oplus-framework/smali/com/oplus/multiapp/OplusMultiAppManager.smali": "getMultiAppUserHandle()Landroid/os/UserHandle;",
        "work/oplus-framework/smali/com/oplus/wrapper/content/pm/UserInfo.smali": "<init>(Landroid/content/pm/UserInfo;)V",
        "work/framework/smali/android/app/AppGlobals.smali": "getInitialApplication()Landroid/app/Application;",
        "work/framework/smali/android/content/Context.smali": "getSystemService(Ljava/lang/Class;)Ljava/lang/Object;",
        "work/framework/smali_classes3/android/os/UserHandle.smali": "getIdentifier()I",
        "work/framework/smali_classes3/android/os/UserManager.smali": "getUserInfo(I)Landroid/content/pm/UserInfo;",
    }
    for path, signature in dependencies.items():
        assert any(line.startswith(".method public ") and line.endswith(signature)
                   for line in (ROOT / path).read_text(encoding="utf-8").splitlines()), signature
    print("PASS: only classes2.dex content changed; original input unchanged")
    print("PASS: ZIP CRCs, all DEX SHA1/Adler32 checksums, stored-entry alignment")
    print("PASS: all 5 assembled calls redirected; replacement APIs exist in supplied frameworks")
    print("SHA256:", hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
