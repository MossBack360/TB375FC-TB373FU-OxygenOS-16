"""Build the reversible postboot OnePlus international account overlay."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "patch/account-global-overlay"
APK = ROOT / "out/account-investigation-2026-09-07/KeKeUserCenter-global-trial.apk"
OUT_DIR = ROOT / "out/global-account-overlay-2026-09-08"
OUT = OUT_DIR / "fixo-global-account-v1.0-magisk.zip"
APK_SHA256 = "8a667d7ea830319735beb43878f93b76604bb7a776ec3f6a033d2414281d9d4d"


def add(archive: ZipFile, name: str, data: bytes, executable: bool = False) -> None:
    info = ZipInfo(name)
    info.external_attr = (0o100755 if executable else 0o100644) << 16
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, data)


def main() -> None:
    apk = APK.read_bytes()
    assert sha256(apk).hexdigest() == APK_SHA256
    service = (SRC / "service.sh").read_bytes().replace(b"\r\n", b"\n")
    module_prop = (SRC / "module.prop").read_bytes().replace(b"\r\n", b"\n")
    assert b"\r" not in service

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w") as archive:
        add(archive, "module.prop", module_prop)
        add(archive, "service.sh", service, executable=True)
        add(archive, "payload/KeKeUserCenter.apk", apk)

    with ZipFile(OUT) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == [
            "module.prop",
            "service.sh",
            "payload/KeKeUserCenter.apk",
        ]

    digest = sha256(OUT.read_bytes()).hexdigest().upper()
    (OUT_DIR / "SHA256SUMS.txt").write_text(
        f"{digest}  {OUT.name}\n", encoding="ascii"
    )
    print(OUT)
    print(digest)


if __name__ == "__main__":
    main()
