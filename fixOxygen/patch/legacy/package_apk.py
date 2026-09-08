"""Replace only classes2.dex; preserve file contents and align stored entries."""
from pathlib import Path
import copy
import struct
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SIGNATURES = {"META-INF/CERT.RSA", "META-INF/CERT.SF", "META-INF/MANIFEST.MF"}


def main():
    dex = (ROOT / "work/assemble/build/apk/classes2.dex").read_bytes()
    output = ROOT / "out/Settings-fixed-unsigned.apk"
    with zipfile.ZipFile(ROOT / "extract/Settings.apk") as original, zipfile.ZipFile(output, "w") as patched:
        for entry in original.infolist():
            if entry.filename in SIGNATURES:
                continue
            info = copy.copy(entry)
            # Existing padding describes old offsets; generate fresh ZIP extra padding.
            info.extra = b""
            if info.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if info.filename.startswith("lib/") and info.filename.endswith(".so") else 4
                data_offset = patched.fp.tell() + 30 + len(info.filename.encode("utf-8"))
                if data_offset % alignment:
                    padding = (-data_offset - 4) % alignment
                    info.extra = struct.pack("<HH", 0xFFFF, padding) + bytes(padding)
            patched.writestr(info, dex if info.filename == "classes2.dex" else original.read(entry))
    print(output)


if __name__ == "__main__":
    main()
