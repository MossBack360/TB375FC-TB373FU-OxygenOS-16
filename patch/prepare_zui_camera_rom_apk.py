"""Prepare an offline ZuiCamera v2 candidate with the ROM APK signer identity.

The copied v3 signing block does not make the patched APK independently valid.
This candidate is for a later system-partition scan test, not direct install.
"""

from hashlib import sha256
from pathlib import Path
from struct import pack_into, unpack_from
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT.parent / "temp3/OxygenOS_16.0.5_TB373FU_TB375FC_v2/v3/filesystems/system_a/system_a/system/priv-app/ZuiCamera/ZuiCamera.apk"
PATCHED = ROOT / "out/zui-camera-sr-runtime-fix-v2.0-2026-09-14/ZuiCamera-sr-runtime-fix-v2.apk"
OUT_DIR = ROOT / "out/zui-camera-rom-scan-2026-11-13"
OUT = OUT_DIR / "ZuiCamera-v2-rom-signing-block-candidate.apk"
ROM_SHA = "6752402e1d1f2308941d50aaf056f9a69246337884f7cc1b9a7905b9f5f2c9ba"
PATCHED_SHA = "42e55eb755521791ac757e6c8ca1d0b1c6b6fcdf02e7a29004a126fcface1676"
MAGIC = b"APK Sig Block 42"


def central_directory(data: bytes) -> tuple[int, int]:
    eocd = data.rfind(b"PK\x05\x06")
    assert eocd >= 0 and eocd + 22 <= len(data)
    assert eocd + 22 + unpack_from("<H", data, eocd + 20)[0] == len(data)
    assert unpack_from("<H", data, eocd + 10)[0] != 0xFFFF
    offset = unpack_from("<I", data, eocd + 16)[0]
    assert data[offset : offset + 4] == b"PK\x01\x02"
    return offset, eocd


def main() -> None:
    rom = ROM.read_bytes()
    patched = PATCHED.read_bytes()
    assert sha256(rom).hexdigest() == ROM_SHA
    assert sha256(patched).hexdigest() == PATCHED_SHA

    rom_cd, _ = central_directory(rom)
    size = unpack_from("<Q", rom, rom_cd - 24)[0]
    assert rom[rom_cd - 16 : rom_cd] == MAGIC
    block_start = rom_cd - size - 8
    assert unpack_from("<Q", rom, block_start)[0] == size
    block = rom[block_start:rom_cd]

    patched_cd, patched_eocd = central_directory(patched)
    assert patched[patched_cd - 16 : patched_cd] != MAGIC
    candidate = bytearray(patched[:patched_cd] + block + patched[patched_cd:])
    pack_into("<I", candidate, patched_eocd + len(block) + 16, patched_cd + len(block))
    assert central_directory(candidate)[0] == patched_cd + len(block)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(candidate)
    with ZipFile(PATCHED) as old, ZipFile(OUT) as new:
        assert old.namelist() == new.namelist()
        assert all(old.getinfo(name).CRC == new.getinfo(name).CRC for name in old.namelist())

    (OUT_DIR / "SHA256SUMS.txt").write_text(
        f"{sha256(candidate).hexdigest().upper()}  {OUT.name}\n", encoding="ascii"
    )
    print(f"candidate={OUT}")
    print(f"signing_block_bytes={len(block)}")
    print(f"candidate_sha256={sha256(candidate).hexdigest()}")


if __name__ == "__main__":
    main()
