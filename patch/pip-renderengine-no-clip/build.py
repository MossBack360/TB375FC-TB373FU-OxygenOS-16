#!/usr/bin/env python3
"""Build the verified TB375FC OOS16 PiP RenderEngine Magisk module."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


SOURCE_SHA256 = "dc12fd204d76591d231ae3f62034779112c25b664593f2aa110ce2ac460acd35"
PATCHED_SHA256 = "7c5c7c37234886135482c69fc0bbc50b3b2b9ca8f38544d12ccc7df0336de895"
OFFSET = 0x1A3A80
ORIGINAL = bytes.fromhex("c8 23 00 b0")
RETURN = bytes.fromhex("c0 03 5f d6")  # AArch64 ret
PAYLOAD = "system/system_ext/lib64/librenderengineextimpl.so"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stock", type=Path, help="Unmodified OOS16 librenderengineextimpl.so")
    parser.add_argument("output", type=Path, help="Output Magisk ZIP")
    args = parser.parse_args()

    stock = args.stock.read_bytes()
    assert digest(stock) == SOURCE_SHA256, "Unexpected ROM library; refusing to patch"
    assert stock[OFFSET : OFFSET + 4] == ORIGINAL, "Unexpected function entry"
    patched = stock[:OFFSET] + RETURN + stock[OFFSET + 4 :]
    assert digest(patched) == PATCHED_SHA256, "Patched library differs from confirmed test"

    metadata = (
        "id=fixo_pip_renderengine_no_clip\n"
        "name=TB375FC PiP rounded corner render fix\n"
        "version=1.0\nversionCode=1\nauthor=MossBack360\n"
        "description=Skip OPlus forceNoClipSmooth radius rewrite in RenderEngine.\n"
    )
    guard = (
        "#!/system/bin/sh\n"
        "base=/system_ext/lib64/librenderengineextimpl.so\n"
        "actual=$(sha256sum \"$base\" 2>/dev/null)\n"
        f"case \"$actual\" in '{SOURCE_SHA256} '*) ;; "
        "*) abort \"Unsupported RenderEngine library; module not installed\" ;; esac\n"
    )
    readme = (
        "TB375FC OOS16 PiP rounded corner fix v1.0\n"
        "Changes only forceNoClipSmooth() entry at file offset 0x1a3a80 to AArch64 RET.\n"
        "This bypasses the OPlus radius rewrite for all layers; other library code is unchanged.\n"
        "Remove/disable this module and reboot to restore the stock library.\n"
        f"Stock SHA-256: {SOURCE_SHA256}\nPatched SHA-256: {PATCHED_SHA256}\n"
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr("module.prop", metadata)
        archive.writestr("customize.sh", guard)
        archive.writestr("README.txt", readme)
        archive.writestr(PAYLOAD, patched)

    with ZipFile(args.output) as archive:
        names = archive.namelist()
        assert PAYLOAD in names and all("\\" not in name for name in names)
        assert digest(archive.read(PAYLOAD)) == PATCHED_SHA256
    print(args.output)
    print(f"module ZIP SHA-256: {digest(args.output.read_bytes())}")


if __name__ == "__main__":
    main()
