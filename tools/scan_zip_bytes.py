import pathlib
import sys
import zipfile


needle = sys.argv[1].encode()
for root in map(pathlib.Path, sys.argv[2:]):
    for path in root.rglob("*"):
        if path.suffix.lower() not in {".apk", ".jar"}:
            continue
        try:
            with zipfile.ZipFile(path) as archive:
                for entry in archive.infolist():
                    if entry.filename.endswith(".dex") and needle in archive.read(entry):
                        print(f"{path}\t{entry.filename}")
        except (OSError, zipfile.BadZipFile):
            pass
