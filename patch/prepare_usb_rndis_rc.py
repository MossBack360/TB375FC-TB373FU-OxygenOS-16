"""Stage the one-action USB tethering fix from the untouched v2 init RC."""

from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT.parent / "temp3/OxygenOS_16.0.5_TB373FU_TB375FC_v2/v3/originals-before-v3/init.usb.configfs.rc.original"
OUT_DIR = ROOT / "out/rom-solidification-prep-2026-11-13"
OUT = OUT_DIR / "init.usb.configfs.rc"
EXPECTED_SHA = "87ffc530d89c587a8b3751e1ad66ec0bae365753421d4a0c72af20eab62b8d6b"


def main() -> None:
    original = ORIGINAL.read_bytes()
    assert sha256(original).hexdigest() == EXPECTED_SHA
    anchor = b"on property:sys.usb.config=mtp && property:sys.usb.configfs=1"
    action = (
        b"on property:sys.usb.config=rndis,adb && property:sys.usb.configfs=1\n"
        b"    start adbd\n\n"
    )
    assert original.count(anchor) == 1
    assert b"on property:sys.usb.config=rndis,adb" not in original
    result = original.replace(anchor, action + anchor)
    assert len(result) == len(original) + len(action)
    assert result.count(b"on property:sys.usb.config=rndis,adb") == 1
    assert b"sys.usb.ffs.ready=1 && property:sys.usb.config=rndis,adb" not in result
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(result)
    print(f"staged={OUT}")
    print(f"sha256={sha256(result).hexdigest()}")


if __name__ == "__main__":
    main()
