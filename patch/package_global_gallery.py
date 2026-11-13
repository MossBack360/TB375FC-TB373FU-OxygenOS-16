"""Build the Gallery-only successor to fixo_global_apps v1.0."""

from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "patch/global-gallery-overlay"
GALLERY = ROOT / "out/global-apps-2026-09-07/Gallery-before.apk"
EXPECTED_GALLERY_SHA256 = "5be668588f05e182d4164693ba7affe7658b394833ce2445cbeab5de529229ad"
OUT_DIR = ROOT / "out/global-gallery-overlay-v1.1-2026-11-13"
OUT = OUT_DIR / "02-global-apps-gallery-v1.1-gallery-only.zip"


def add(archive: ZipFile, name: str, data: bytes, executable: bool = False) -> None:
    info = ZipInfo(name)
    info.external_attr = (0o100755 if executable else 0o100644) << 16
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, data)


def main() -> None:
    gallery = GALLERY.read_bytes()
    assert sha256(gallery).hexdigest() == EXPECTED_GALLERY_SHA256
    service = (SRC / "service.sh").read_bytes().replace(b"\r\n", b"\n")
    module_prop = (SRC / "module.prop").read_bytes().replace(b"\r\n", b"\n")
    assert b"KeKeUserCenter" not in service + module_prop

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w") as archive:
        add(archive, "module.prop", module_prop)
        add(archive, "service.sh", service, executable=True)
        add(archive, "payload/OppoGallery2.apk", gallery)

    with ZipFile(OUT) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == ["module.prop", "service.sh", "payload/OppoGallery2.apk"]
        assert all("\\" not in name for name in archive.namelist())

    digest = sha256(OUT.read_bytes()).hexdigest().upper()
    (OUT_DIR / "SHA256SUMS.txt").write_text(f"{digest}  {OUT.name}\n", encoding="ascii")
    print(OUT)
    print(digest)


if __name__ == "__main__":
    main()
