"""Package the corrected isolated contour glow UXDesign trial."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "work/oxygen-ui-current-2026-09-09/UXDesign.apk"
PAYLOAD = ROOT / "work/oxygen-ui-stroke-trial-2026-09-10/UXDesign-stroke-trial.apk"
DEST = ROOT / "out/material-stroke-trial-v2-2026-09-10"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(zf: zipfile.ZipFile, name: str, data: bytes, mode: int) -> None:
    info = zipfile.ZipInfo(name)
    info.external_attr = mode << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, data)


def main() -> None:
    assert SRC.exists() and PAYLOAD.exists()
    assert not DEST.exists(), "Refusing to overwrite an existing package"
    DEST.mkdir(parents=True)
    entries = {
        "module.prop": (ROOT / "patch/material-stroke/module.prop").read_bytes().replace(b"0.1-trial", b"0.2-trial").replace(b"versionCode=1", b"versionCode=2"),
        "service.sh": (ROOT / "patch/material-stroke/service.sh").read_bytes().replace(b"\r\n", b"\n"),
        "README.md": (ROOT / "patch/material-stroke/README.md").read_bytes().replace(b"\r\n", b"\n"),
        "system/system_ext/app/UXDesign/UXDesign.apk": SRC.read_bytes(),
        "payload/UXDesign.apk": PAYLOAD.read_bytes(),
    }
    output = DEST / "fixo-material-stroke-trial-v2-magisk.zip"
    with zipfile.ZipFile(output, "w") as zf:
        for name, data in entries.items():
            add(zf, name, data, 0o100755 if name == "service.sh" else 0o100644)
    with zipfile.ZipFile(output) as zf:
        assert zf.testzip() is None
        assert set(zf.namelist()) == set(entries)
    (DEST / "SHA256SUMS.txt").write_text(f"{sha(output)}  {output.name}\n", encoding="utf-8")
    (DEST / "BASE-HASHES.txt").write_text(f"base UXDesign.apk  {sha(SRC)}\ntrial UXDesign.apk {sha(PAYLOAD)}\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
