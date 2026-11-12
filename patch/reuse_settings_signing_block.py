"""Offline candidate: keep the ROM Settings v3 signing block on the v5.3 payload.

The system-partition scanner may collect its signer without checking the APK
content digest. This file is for analysis only; it is not a verified ROM fix.
"""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "out/settings-signature-audit-2026-11-12"
ROM = AUDIT / "Settings-rom.apk"
PATCHED = AUDIT / "Settings-patched-v5.3.apk"
OUTPUT = AUDIT / "Settings-v5.3-rom-signing-block-candidate.apk"
ROM_SHA = "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"
PATCHED_SHA = "fe8b6161f642fbbacc5eb54646f5b5040afbfa93ca999de967f7013041369bcb"
MAGIC = b"APK Sig Block 42"
EOCD = b"PK\x05\x06"


def central_directory(data: bytes) -> tuple[int, int]:
    eocd = data.rfind(EOCD)
    assert eocd >= 0 and eocd + 22 <= len(data)
    assert eocd + 22 + struct.unpack_from("<H", data, eocd + 20)[0] == len(data)
    assert struct.unpack_from("<H", data, eocd + 10)[0] != 0xFFFF
    offset = struct.unpack_from("<I", data, eocd + 16)[0]
    assert data[offset : offset + 4] == b"PK\x01\x02"
    return offset, eocd


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


rom = ROM.read_bytes()
patched = PATCHED.read_bytes()
assert digest(rom) == ROM_SHA
assert digest(patched) == PATCHED_SHA
rom_cd, _ = central_directory(rom)
size = struct.unpack_from("<Q", rom, rom_cd - 24)[0]
assert rom[rom_cd - 16 : rom_cd] == MAGIC
block_start = rom_cd - size - 8
assert struct.unpack_from("<Q", rom, block_start)[0] == size
block = rom[block_start:rom_cd]

patched_cd, patched_eocd = central_directory(patched)
assert patched[patched_cd - 16 : patched_cd] != MAGIC
candidate = bytearray(patched[:patched_cd] + block + patched[patched_cd:])
struct.pack_into("<I", candidate, patched_eocd + len(block) + 16, patched_cd + len(block))
assert central_directory(candidate)[0] == patched_cd + len(block)
OUTPUT.write_bytes(candidate)

with ZipFile(PATCHED) as original, ZipFile(OUTPUT) as result:
    assert original.namelist() == result.namelist()
    for name in original.namelist():
        assert original.getinfo(name).CRC == result.getinfo(name).CRC

print(f"candidate={OUTPUT}")
print(f"signing_block_bytes={len(block)}")
print(f"candidate_sha256={digest(candidate)}")
