"""Package Settings with the ColorOS outline removed from the easter egg."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "out/settings-no-coloros-easter-test-2026-09-08"
ORIGINAL_HASH = "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"


def main() -> None:
    original = (ROOT / "extract/Settings.apk").read_bytes()
    fixed = (DEST / "Settings-blue-red-no-coloros-easter.apk").read_bytes()
    assert hashlib.sha256(original).hexdigest() == ORIGINAL_HASH
    service = (ROOT / "patch/settings-postboot-service.sh").read_bytes().replace(b"\r\n", b"\n")
    entries = {
        "module.prop": b"id=fixo_settings_confirmed\nname=Confirmed Settings plus clean OxygenOS easter egg\nversion=3.5\nversionCode=8\nauthor=local\ndescription=Stable fixes, blue-red OxygenOS card, and confetti animation without the baked ColorOS outline.\n",
        "service.sh": service,
        "system/system_ext/priv-app/Settings/Settings.apk": original,
        "payload/Settings.apk": fixed,
    }
    output = DEST / "fixo-settings-no-coloros-easter-magisk.zip"
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
