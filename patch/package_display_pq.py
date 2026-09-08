from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "patch" / "display-pq-controller"
JAR = ROOT / "work" / "fixo-display-pq.jar"
OUT = ROOT / "out" / "display-pq-bridge-2026-09-08"
ZIP_PATH = OUT / "fixo-display-pq-v1.0-magisk.zip"


def main() -> None:
    if not JAR.is_file():
        raise FileNotFoundError(JAR)
    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(ZIP_PATH, "w", ZIP_DEFLATED) as archive:
        for name, mode in (("module.prop", 0o100644), ("service.sh", 0o100755), ("README.md", 0o100644)):
            info = ZipInfo(name)
            info.external_attr = mode << 16
            archive.writestr(info, (SRC / name).read_bytes().replace(b"\r\n", b"\n"))
        info = ZipInfo("pqctl.jar")
        info.external_attr = 0o100644 << 16
        archive.writestr(info, JAR.read_bytes())

    digest = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest().upper()
    (OUT / "SHA256SUMS.txt").write_text(f"{digest}  {ZIP_PATH.name}\n", encoding="ascii")
    print(ZIP_PATH)
    print(digest)


if __name__ == "__main__":
    main()
