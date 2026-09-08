"""Build the postboot global account + gallery Magisk overlay."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "patch/global-apps-overlay"
ACCOUNT_APK = ROOT / "out/account-investigation-2026-09-07/KeKeUserCenter-global-trial.apk"
GALLERY_APK = ROOT / "out/global-apps-2026-09-07/Gallery-before.apk"
OUT_DIR = ROOT / "out/global-apps-overlay-2026-09-08"
OUT = OUT_DIR / "fixo-global-apps-v1.0-magisk.zip"
ACCOUNT_SHA256 = "8a667d7ea830319735beb43878f93b76604bb7a776ec3f6a033d2414281d9d4d"
GALLERY_SHA256 = "5be668588f05e182d4164693ba7affe7658b394833ce2445cbeab5de529229ad"


def add(archive: ZipFile, name: str, data: bytes, executable: bool = False) -> None:
    info = ZipInfo(name)
    info.external_attr = (0o100755 if executable else 0o100644) << 16
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, data)


def main() -> None:
    account = ACCOUNT_APK.read_bytes()
    gallery = GALLERY_APK.read_bytes()
    assert sha256(account).hexdigest() == ACCOUNT_SHA256
    assert sha256(gallery).hexdigest() == GALLERY_SHA256

    service = (SRC / "service.sh").read_bytes().replace(b"\r\n", b"\n")
    module_prop = (SRC / "module.prop").read_bytes().replace(b"\r\n", b"\n")
    assert b"\r" not in service

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w") as archive:
        add(archive, "module.prop", module_prop)
        add(archive, "service.sh", service, executable=True)
        add(archive, "payload/KeKeUserCenter.apk", account)
        add(archive, "payload/OppoGallery2.apk", gallery)

    with ZipFile(OUT) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == [
            "module.prop",
            "service.sh",
            "payload/KeKeUserCenter.apk",
            "payload/OppoGallery2.apk",
        ]

    digest = sha256(OUT.read_bytes()).hexdigest().upper()
    (OUT_DIR / "SHA256SUMS.txt").write_text(
        f"{digest}  {OUT.name}\n", encoding="ascii"
    )
    (OUT_DIR / "README.md").write_text(
        "fixo-global-apps-v1.0-magisk.zip\n"
        "\n"
        f"- KeKeUserCenter.apk SHA256: {ACCOUNT_SHA256.upper()}\n"
        f"- OppoGallery2.apk SHA256: {GALLERY_SHA256.upper()}\n"
        "- Account source: OPD global donor, verified launchable on device.\n"
        "- Gallery source: current backed-up OnePlus export build 16.35.10.\n",
        encoding="ascii",
    )
    print(OUT)
    print(digest)


if __name__ == "__main__":
    main()
