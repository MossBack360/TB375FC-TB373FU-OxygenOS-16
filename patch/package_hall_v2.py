"""Archive the Settings-linked hall-cover Magisk module without touching v1."""
from pathlib import Path
import hashlib
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hall-v2"
DEST = ROOT / "out/hall-settings-linked-confirmed-2026-09-08"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if DEST.exists():
        raise SystemExit(f"Refusing to overwrite {DEST}")
    assert b"\r" not in (SRC / "service.sh").read_bytes()
    DEST.mkdir(parents=True)
    for name in ("service.sh", "module.prop", "README.md"):
        shutil.copy2(SRC / name, DEST / name)
    output = DEST / "xiaoxin-hall-settings-linked-v2-magisk.zip"
    with zipfile.ZipFile(output, "w") as archive:
        for name, mode in (("module.prop", 0o100644), ("service.sh", 0o100755)):
            info = zipfile.ZipInfo(name)
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (SRC / name).read_bytes())
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert (archive.getinfo("service.sh").external_attr >> 16) & 0o777 == 0o755
    (DEST / "SHA256SUMS.txt").write_text("".join(f"{digest(p)}  {p.name}\n" for p in sorted(DEST.iterdir()) if p.is_file()), encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
