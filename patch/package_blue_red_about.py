"""Package the blue-red About-device card test build as a post-boot Magisk overlay."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "out/settings-blue-red-card-confirmed-2026-09-08"
ORIGINAL_HASH = "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"


def main() -> None:
    original = (ROOT / "extract/Settings.apk").read_bytes()
    fixed = (DEST / "Settings-global-polish-blue-red-card.apk").read_bytes()
    assert hashlib.sha256(original).hexdigest() == ORIGINAL_HASH
    service = (ROOT / "patch/settings-postboot-service.sh").read_bytes().replace(b"\r\n", b"\n")
    entries = {
        "module.prop": b"id=fixo_settings_confirmed\nname=Confirmed Settings plus OxygenOS 16 blue-red card\nversion=3.4\nversionCode=7\nauthor=local\ndescription=Stable Settings fixes, global assets, and OxygenOS 16 About-device background.\n",
        "service.sh": service,
        "system/system_ext/priv-app/Settings/Settings.apk": original,
        "payload/Settings.apk": fixed,
    }
    output = DEST / "fixo-settings-blue-red-card-magisk.zip"
    with ZipFile(output, "w") as archive:
        for name, data in entries.items():
            info = ZipInfo(name)
            info.external_attr = (0o100755 if name == "service.sh" else 0o100644) << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == data for name, data in entries.items())
    with (DEST / "SHA256SUMS.txt").open("a", encoding="ascii") as sums:
        sums.write(f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output.name}\n")
    print(output)


if __name__ == "__main__":
    main()
