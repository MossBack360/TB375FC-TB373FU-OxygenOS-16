"""Stage the confirmed early-scan ZuiCamera candidate in v3/v4 ROM trees."""

from hashlib import sha256
from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT.parent / "temp3/OxygenOS_16.0.5_TB373FU_TB375FC_v2"
SOURCE = ROOT / "out/zui-camera-rom-scan-2026-11-13/ZuiCamera-v2-rom-signing-block-candidate.apk"
BACKUP = ROOT / "out/zui-camera-rom-scan-2026-11-13/ZuiCamera-original-before-solidification.apk"
BASE_SHA = "6752402e1d1f2308941d50aaf056f9a69246337884f7cc1b9a7905b9f5f2c9ba"
PATCH_SHA = "7a21a0c3f28b1eb715dbbb9bd4a1be5e3722eef4f998de100c68bd58a4beb862"
BUILD_PROP_SHA = "931b7e51f9e20c257016646e653a9289fe52b052cc1c438265b5794bdFA9C658".lower()
PROPERTY = b"debug.camera.morpho.sr.on=0\n"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert digest(SOURCE) == PATCH_SHA
    targets = []
    for version in ("v3", "v4-cts"):
        system = ROM / version / "filesystems/system_a/system_a/system"
        apk = system / "priv-app/ZuiCamera/ZuiCamera.apk"
        prop = system / "build.prop"
        assert digest(apk) in (BASE_SHA, PATCH_SHA), f"unexpected camera in {version}"
        data = prop.read_bytes()
        assert digest(prop) == BUILD_PROP_SHA or data.count(PROPERTY) == 1, f"unexpected build.prop in {version}"
        assert data.count(PROPERTY) <= 1
        targets.append((version, apk, prop, data))

    if not BACKUP.exists():
        original = next((apk for _, apk, _, _ in targets if digest(apk) == BASE_SHA), None)
        if original is None:
            raise RuntimeError("no original camera available for backup")
        copyfile(original, BACKUP)
    assert digest(BACKUP) == BASE_SHA

    for version, apk, prop, data in targets:
        copyfile(SOURCE, apk)
        if PROPERTY not in data:
            prop.write_bytes(data.rstrip(b"\r\n") + b"\n" + PROPERTY)
        assert digest(apk) == PATCH_SHA
        assert prop.read_bytes().count(PROPERTY) == 1
        print(f"{version}: camera={digest(apk)} property=ok")
    print(f"backup={BACKUP} sha256={digest(BACKUP)}")


if __name__ == "__main__":
    main()
