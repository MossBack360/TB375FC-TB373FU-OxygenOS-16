"""Package the isolated contour glow UXDesign trial as a Magisk module."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "work/oxygen-ui-current-2026-09-09/UXDesign.apk"
PAYLOAD = ROOT / "work/oxygen-ui-stroke-trial-2026-09-10/UXDesign-stroke-trial.apk"
DEST = ROOT / "out/material-stroke-trial-v3-2026-09-10"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(zf: zipfile.ZipFile, name: str, data: bytes, mode: int = 0o100644) -> None:
    info = zipfile.ZipInfo(name)
    info.external_attr = mode << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, data)


def main() -> None:
    assert SRC.exists() and PAYLOAD.exists()
    assert not DEST.exists(), "Refusing to overwrite an existing trial package"
    DEST.mkdir(parents=True)
    prop = (ROOT / "patch/material-stroke/module.prop").read_bytes().replace(b"\r\n", b"\n").replace(b"0.1-trial", b"0.3-trial").replace(b"versionCode=1", b"versionCode=3")
    service = (ROOT / "patch/material-stroke/service.sh").read_bytes().replace(b"\r\n", b"\n")
    readme = (ROOT / "patch/material-stroke/README.md").read_bytes().replace(b"\r\n", b"\n")
    entries = {
        "module.prop": prop,
        "service.sh": service,
        "README.md": readme,
        "system/system_ext/app/UXDesign/UXDesign.apk": SRC.read_bytes(),
        "payload/UXDesign.apk": PAYLOAD.read_bytes(),
    }
    output = DEST / "fixo-material-stroke-trial-v3-magisk.zip"
    with zipfile.ZipFile(output, "w") as zf:
        for name, data in entries.items():
            add(zf, name, data, 0o100755 if name == "service.sh" else 0o100644)
    with zipfile.ZipFile(output) as zf:
        assert zf.testzip() is None
        assert set(zf.namelist()) == set(entries)
    (DEST / "SHA256SUMS.txt").write_text(
        "".join(f"{sha(path)}  {path.name}\n" for path in sorted(DEST.glob("*.zip"))),
        encoding="utf-8",
    )
    (DEST / "BASE-HASHES.txt").write_text(
        f"base UXDesign.apk  {sha(SRC)}\n"
        f"trial UXDesign.apk {sha(PAYLOAD)}\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
