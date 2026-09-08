from hashlib import sha256
from pathlib import Path
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hall"
DEST = ROOT / "out" / "hall-confirmed-2026-09-06"
ZIP_NAME = "xiaoxin-hall-confirmed-magisk.zip"

EXPECTED = {
    "service.sh": "95e498cd3d14d56743d42ee051fd768ccf1e98691592aac2d29f57f334502f88",
    "module.prop": "a7bd2313312ac2c07e71866bfa7e94d105b379c078cd9dae71d47dd4fabf49a7",
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def add_zip_entry(zf: zipfile.ZipFile, src: Path, name: str, mode: int) -> None:
    info = zipfile.ZipInfo(name)
    info.external_attr = (mode & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, src.read_bytes())


def main() -> None:
    if DEST.exists():
        raise SystemExit(f"Refusing to overwrite existing archive: {DEST}")

    for name, expected in EXPECTED.items():
        actual = digest(SRC / name)
        if actual != expected:
            raise SystemExit(f"{name} hash mismatch: {actual}")
        if b"\r\n" in (SRC / name).read_bytes():
            raise SystemExit(f"{name} has CRLF line endings")

    DEST.mkdir(parents=True)
    shutil.copy2(SRC / "service.sh", DEST / "service.sh")
    shutil.copy2(SRC / "module.prop", DEST / "module.prop")
    shutil.copy2(SRC / "README.md", DEST / "README.md")

    zip_path = DEST / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w") as zf:
        add_zip_entry(zf, SRC / "module.prop", "module.prop", 0o100644)
        add_zip_entry(zf, SRC / "service.sh", "service.sh", 0o100755)

    with zipfile.ZipFile(zip_path) as zf:
        entries = {info.filename: info for info in zf.infolist()}
        assert set(entries) == {"module.prop", "service.sh"}
        assert (entries["service.sh"].external_attr >> 16) & 0o777 == 0o755
        assert sha256(zf.read("service.sh")).hexdigest() == EXPECTED["service.sh"]
        assert sha256(zf.read("module.prop")).hexdigest() == EXPECTED["module.prop"]

    targets = [
        DEST / "service.sh",
        DEST / "module.prop",
        DEST / "README.md",
        zip_path,
    ]
    (DEST / "SHA256SUMS.txt").write_text(
        "".join(f"{digest(path)}  {path.name}\n" for path in targets),
        encoding="ascii",
        newline="\n",
    )

    print(DEST)
    print(digest(zip_path))


if __name__ == "__main__":
    main()
