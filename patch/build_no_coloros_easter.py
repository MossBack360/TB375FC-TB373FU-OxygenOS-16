"""Remove the baked ColorOS outline from the About-device Lottie easter egg."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import copy
import hashlib
import io
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "out/settings-blue-red-card-confirmed-2026-09-08/Settings-global-polish-blue-red-card.apk"
DEST = ROOT / "out/settings-no-coloros-easter-test-2026-09-08"
EXPECTED_BASE = "7ecad47e76a810bfe385e012633adb4fa1fd3be16e5aab45a9af4b660f9e94a9"
PREFIX = "about_device_easter_egg_oos"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_logo(bundle: bytes) -> tuple[bytes, int, int]:
    source = ZipFile(io.BytesIO(bundle))
    output = io.BytesIO()
    kept = removed = 0
    with source, ZipFile(output, "w") as result:
        for entry in source.infolist():
            data = source.read(entry)
            if entry.filename.startswith("animations/") and entry.filename.endswith(".json"):
                animation = json.loads(data)
                for asset in animation.get("assets", []):
                    layers = asset.get("layers")
                    if not layers:
                        continue
                    particle_layers = [layer for layer in layers if float(layer.get("op", 0)) <= 100]
                    logo_layers = [layer for layer in layers if float(layer.get("op", 0)) > 100]
                    if not logo_layers:
                        continue
                    kept += len(particle_layers)
                    removed += len(logo_layers)
                    kept_ids = {layer.get("ind") for layer in particle_layers}
                    assert all(layer.get("parent") in (None, 0) or layer.get("parent") in kept_ids
                               for layer in particle_layers)
                    asset["layers"] = particle_layers
                data = json.dumps(animation, ensure_ascii=False, separators=(",", ":")).encode()
            info = copy.copy(entry)
            info.compress_type = ZIP_DEFLATED
            result.writestr(info, data)
    assert kept and removed
    return output.getvalue(), kept, removed


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
    assert sha(BASE.read_bytes()) == EXPECTED_BASE
    replacements = {}
    report = []
    with ZipFile(BASE) as base:
        for name in base.namelist():
            if PREFIX not in name:
                continue
            replacements[name], kept, removed = strip_logo(base.read(name))
            report.append(f"{name}: kept {kept} particle layers, removed {removed} logo layers")
        assert len(replacements) == 8
        DEST.mkdir(parents=True)
        output = DEST / "Settings-blue-red-no-coloros-easter.apk"
        aligned_copy(base, output, replacements)
    with ZipFile(BASE) as base, ZipFile(output) as result:
        assert result.testzip() is None
        changed = {n for n in base.namelist() if base.read(n) != result.read(n)}
        assert changed == set(replacements)
        for name in replacements:
            with ZipFile(io.BytesIO(result.read(name))) as nested:
                assert nested.testzip() is None
    (DEST / "lottie-layer-report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    (DEST / "SHA256SUMS.txt").write_text(f"{sha(output.read_bytes())}  {output.name}\n", encoding="ascii")
    print(output)
    print("\n".join(report))


if __name__ == "__main__":
    main()
