"""Retain the ROM SystemUI signer on the CTS-patched APK for system scan trial."""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(r"E:\工程\github\xiaoxin Oxygen\temp3\OxygenOS_16.0.5_TB373FU_TB375FC_v2\v3\filesystems\system_ext_a\system_ext_a\priv-app\SystemUI\SystemUI.apk")
PATCHED = ROOT / "out/cts-native-v0.1-2026-11-12/SystemUI-cts-dispatch-v0.1.apk"
OUTPUT = ROOT / "out/cts-native-v0.1-2026-11-12/SystemUI-cts-rom-scan-candidate.apk"
BASE_SHA = "72cfa6810c72d7aef8cfdfd8f57ee8f88117c2b5867f272d3700a08fe3c32dc7"
PATCHED_SHA = "58ad7e224d5d5273c4cdceed53259b682788343a4e525a7b89fcdb585644a072"
MAGIC = b"APK Sig Block 42"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def central_directory(data: bytes) -> tuple[int, int]:
    eocd = data.rfind(b"PK\x05\x06")
    assert eocd >= 0 and eocd + 22 <= len(data)
    assert eocd + 22 + struct.unpack_from("<H", data, eocd + 20)[0] == len(data)
    offset = struct.unpack_from("<I", data, eocd + 16)[0]
    assert data[offset:offset + 4] == b"PK\x01\x02"
    return offset, eocd


def main() -> None:
    base = BASE.read_bytes()
    patched = PATCHED.read_bytes()
    assert sha(base) == BASE_SHA
    assert sha(patched) == PATCHED_SHA
    base_cd, _ = central_directory(base)
    size = struct.unpack_from("<Q", base, base_cd - 24)[0]
    assert base[base_cd - 16:base_cd] == MAGIC
    block_start = base_cd - size - 8
    assert struct.unpack_from("<Q", base, block_start)[0] == size
    block = base[block_start:base_cd]
    patched_cd, patched_eocd = central_directory(patched)
    assert patched[patched_cd - 16:patched_cd] != MAGIC
    candidate = bytearray(patched[:patched_cd] + block + patched[patched_cd:])
    struct.pack_into("<I", candidate, patched_eocd + len(block) + 16, patched_cd + len(block))
    assert central_directory(candidate)[0] == patched_cd + len(block)
    OUTPUT.write_bytes(candidate)
    with ZipFile(PATCHED) as original, ZipFile(OUTPUT) as result:
        assert original.namelist() == result.namelist()
        assert all(original.getinfo(n).CRC == result.getinfo(n).CRC for n in original.namelist())
    print(f"candidate={OUTPUT}")
    print(f"signing_block_bytes={len(block)}")
    print(f"candidate_sha256={sha(candidate)}")


if __name__ == "__main__":
    main()
