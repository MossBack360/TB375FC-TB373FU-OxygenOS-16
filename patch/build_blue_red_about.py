"""Replace only the About-device card frames with the OxygenOS 16 OTA artwork."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import copy
import hashlib
import io
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "out/settings-global-polish-confirmed-2026-09-08/Settings-global-avatar-oxygen-logo.apk"
SOURCE = ROOT / "work/ota-code/unknown/res/h8.webp"
DEST = ROOT / "out/settings-blue-red-card-confirmed-2026-09-08"
EXPECTED_BASE = "0ae42565af5f83cecf2d9cb0246959d3ee066c8d4f9c8e1e30d5867cfe74d348"
TARGET = "about_device_top_video_last_frame"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cover(source: Image.Image, size: tuple[int, int]) -> bytes:
    sw, sh = source.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    resized = source.resize((round(sw * scale), round(sh * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - tw) // 2
    top = (resized.height - th) // 2
    image = resized.crop((left, top, left + tw, top + th))
    output = io.BytesIO()
    image.save(output, "WEBP", quality=92, method=6)
    return output.getvalue()


def aligned_copy(base: ZipFile, output: Path, replacements: dict[str, bytes]) -> None:
    with ZipFile(output, "w") as result:
        for entry in base.infolist():
            info = copy.copy(entry)
            info.extra = b""
            if info.compress_type == 0:
                alignment = 16384 if info.filename.startswith("lib/") and info.filename.endswith(".so") else 4
                offset = result.fp.tell() + 30 + len(info.filename.encode())
                if offset % alignment:
                    padding = (-offset - 4) % alignment
                    info.extra = struct.pack("<HH", 0xFFFF, padding) + bytes(padding)
            result.writestr(info, replacements.get(entry.filename, base.read(entry)))


def main() -> None:
    if DEST.exists():
        raise SystemExit(f"Refusing to overwrite {DEST}")
    base_data = BASE.read_bytes()
    assert sha(base_data) == EXPECTED_BASE
    source = Image.open(SOURCE).convert("RGB")
    replacements = {}
    with ZipFile(BASE) as base:
        for name in base.namelist():
            if TARGET not in name:
                continue
            old = Image.open(io.BytesIO(base.read(name)))
            replacements[name] = cover(source, old.size)
        assert len(replacements) == 5
        DEST.mkdir(parents=True)
        output = DEST / "Settings-global-polish-blue-red-card.apk"
        aligned_copy(base, output, replacements)
    with ZipFile(BASE) as base, ZipFile(output) as result:
        assert result.testzip() is None
        changed = {n for n in base.namelist() if base.read(n) != result.read(n)}
        assert changed == set(replacements)
    (DEST / "changed-resources.txt").write_text("\n".join(sorted(replacements)) + "\n", encoding="utf-8")
    (DEST / "SHA256SUMS.txt").write_text(f"{sha(output.read_bytes())}  {output.name}\n", encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
