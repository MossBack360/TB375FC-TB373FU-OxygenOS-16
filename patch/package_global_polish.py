"""Package the global Settings polish as a post-boot Magisk overlay."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "out/settings-global-polish-confirmed-2026-09-08"
ORIGINAL_HASH = "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"


def main() -> None:
    original = (ROOT / "extract/Settings.apk").read_bytes()
    fixed_path = DEST / "Settings-global-avatar-oxygen-logo.apk"
    fixed = fixed_path.read_bytes()
    assert hashlib.sha256(original).hexdigest() == ORIGINAL_HASH
    service = (ROOT / "patch/settings-postboot-service.sh").read_bytes().replace(b"\r\n", b"\n")
    entries = {
        "module.prop": b"id=fixo_settings_confirmed\nname=Confirmed Settings - global avatar and OxygenOS card\nversion=3.3\nversionCode=6\nauthor=local\ndescription=Stable Settings plus global default avatar and OxygenOS About-device logo.\n",
        "service.sh": service,
        "system/system_ext/priv-app/Settings/Settings.apk": original,
        "payload/Settings.apk": fixed,
    }
    output = DEST / "fixo-settings-global-polish-magisk.zip"
    if output.exists():
        raise SystemExit(f"Refusing to overwrite {output}")
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(name)
            info.external_attr = (0o100755 if name == "service.sh" else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == data for name, data in entries.items())
    sums = DEST / "SHA256SUMS.txt"
    sums.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in sorted(DEST.glob("*.apk")))
                    + f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output.name}\n", encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
