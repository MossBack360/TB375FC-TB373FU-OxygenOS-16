"""Archive the confirmed Settings APK and build a post-boot Magisk module."""
from pathlib import Path
import hashlib
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "out/confirmed-2026-09-06"
EXPECTED = "6d92c4dc3e3d7b169c57592e673eb4077a6f9fd503fe7fba7608ec771af8ebce"
ORIGINAL = ROOT / "extract/Settings.apk"
POSTBOOT_PAYLOAD = ROOT / "out/settings-easter-logo-only-2026-09-08/Settings-easter-oxygen-logo.apk"


def main():
    source = ROOT / "out/Settings-fixed-system-overlay.apk"
    assert hashlib.file_digest(source.open("rb"), "sha256").hexdigest() == EXPECTED
    DEST.mkdir(exist_ok=False)
    apk = DEST / "Settings.apk"
    shutil.copy2(source, apk)
    shutil.copytree(ROOT / "patch", DEST / "patch", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "reports/current-vs-xiaoxin.patch", DEST / "current-vs-xiaoxin.patch")
    shutil.copy2(ROOT / "reports/confirmed-release-notes.md", DEST / "README.md")
    # Keep the original signed APK visible during package scanning.  Directly
    # replacing Settings.apk at boot makes PackageManager drop
    # com.android.settings on this ROM.  The tested service binds the patched
    # payload only after sys.boot_completed.
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"
    assert POSTBOOT_PAYLOAD.exists()
    service = (ROOT / "patch/settings-postboot-service.sh").read_bytes().replace(b"\r\n", b"\n")
    payload = POSTBOOT_PAYLOAD.read_bytes()
    module = DEST / "fixo-settings-confirmed-magisk.zip"
    prop = (
        "id=fixo_settings_confirmed\n"
        "name=Settings - OxygenOS card and easter egg logo\n"
        "version=3.6\nversionCode=9\nauthor=local\n"
        "description=Keeps the signed Settings APK for package scanning, then applies the tested OxygenOS Settings payload after boot.\n"
    )
    with zipfile.ZipFile(module, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("module.prop", prop)
        info = zipfile.ZipInfo("service.sh")
        info.external_attr = 0o100755 << 16
        z.writestr(info, service)
        z.write(ORIGINAL, "system/system_ext/priv-app/Settings/Settings.apk")
        z.writestr("payload/Settings.apk", payload)
    with zipfile.ZipFile(module) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read("payload/Settings.apk")).hexdigest() == hashlib.sha256(payload).hexdigest()
    with zipfile.ZipFile(ROOT / "extract/Settings.apk") as original, zipfile.ZipFile(apk) as fixed:
        assert fixed.testzip() is None
        assert set(original.namelist()) == set(fixed.namelist())
        assert [n for n in original.namelist() if original.read(n) != fixed.read(n)] == ["classes2.dex"]
    hashes = []
    for p in sorted(DEST.rglob("*")):
        if p.is_file():
            with p.open("rb") as stream:
                hashes.append(f"{hashlib.file_digest(stream, 'sha256').hexdigest()}  {p.relative_to(DEST).as_posix()}\n")
    (DEST / "SHA256SUMS.txt").write_text("".join(hashes), encoding="utf-8")
    print("Archived confirmed APK and uninstalled Magisk module:", DEST)
    print("APK SHA256:", EXPECTED)


if __name__ == "__main__":
    main()
