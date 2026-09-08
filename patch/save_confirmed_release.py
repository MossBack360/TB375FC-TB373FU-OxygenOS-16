"""Archive the exact APK confirmed working on the device; no device writes."""
from pathlib import Path
import hashlib
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "out/confirmed-2026-09-06"
EXPECTED = "6d92c4dc3e3d7b169c57592e673eb4077a6f9fd503fe7fba7608ec771af8ebce"


def main():
    source = ROOT / "out/Settings-fixed-system-overlay.apk"
    assert hashlib.file_digest(source.open("rb"), "sha256").hexdigest() == EXPECTED
    DEST.mkdir(exist_ok=False)
    apk = DEST / "Settings.apk"
    shutil.copy2(source, apk)
    shutil.copytree(ROOT / "patch", DEST / "patch", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "reports/current-vs-xiaoxin.patch", DEST / "current-vs-xiaoxin.patch")
    shutil.copy2(ROOT / "reports/confirmed-release-notes.md", DEST / "README.md")
    module = DEST / "fixo-settings-confirmed-magisk.zip"
    prop = (
        "id=fixo_settings_confirmed\n"
        "name=Xiaoxin Settings compatibility fix (confirmed APK)\n"
        "version=2026.09.06\nversionCode=1\nauthor=local\n"
        "description=TB375FC current OxygenOS ROM: fix missing clone-profile API in Settings. APK runtime tested; module reboot validation pending.\n"
    )
    with zipfile.ZipFile(module, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("module.prop", prop)
        z.write(apk, "system/system_ext/priv-app/Settings/Settings.apk")
    with zipfile.ZipFile(module) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read("system/system_ext/priv-app/Settings/Settings.apk")).hexdigest() == EXPECTED
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
