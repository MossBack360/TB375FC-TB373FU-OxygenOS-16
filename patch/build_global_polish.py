"""Apply the two verified global Settings assets on top of the stable payload."""
from pathlib import Path
import copy
import hashlib
import struct
import zipfile

from build_oxygen_icons import public_ids

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "out/reboot-confirmed-2026-09-07/fixo-settings-postboot-v2-magisk.zip"
DONOR = ROOT / "extract/opd2403 oxygen os settings/Settings.apk"
CURRENT_RES = ROOT / "work/icons-current/res"
DONOR_RES = ROOT / "work/icons-oxygen/res"
DEST = ROOT / "out/settings-global-polish-confirmed-2026-09-08"
EXPECTED_BASE = "268d650808b6a7b23061f298d54549787dabe69ca6f1ef99e3072e85abccbf97"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def aligned_copy(base: zipfile.ZipFile, output: Path, replacements: dict[str, bytes]) -> None:
    with zipfile.ZipFile(output, "w") as result:
        for entry in base.infolist():
            info = copy.copy(entry)
            info.extra = b""
            if info.compress_type == zipfile.ZIP_STORED:
                alignment = 16384 if info.filename.startswith("lib/") and info.filename.endswith(".so") else 4
                offset = result.fp.tell() + 30 + len(info.filename.encode())
                if offset % alignment:
                    padding = (-offset - 4) % alignment
                    info.extra = struct.pack("<HH", 0xFFFF, padding) + bytes(padding)
            result.writestr(info, replacements.get(entry.filename, base.read(entry)))


def remap_xml(raw: bytes, mapping: dict[int, int], colors: dict[int, int] | None = None) -> bytes:
    """Remap package resources and turn donor-only color refs into literal ARGB values."""
    colors = colors or {}
    data = bytearray(raw)
    kind, header, size = struct.unpack_from("<HHI", data)
    assert kind == 3 and size == len(data)

    def replace(offset: int, type_offset: int | None = None) -> None:
        value = struct.unpack_from("<I", data, offset)[0]
        if value in colors and type_offset is not None:
            data[type_offset] = 0x1C  # TYPE_INT_COLOR_ARGB8
            struct.pack_into("<I", data, offset, colors[value])
        elif value >> 24 == 0x7F:
            assert value in mapping, f"Unmapped resource: {value:#x}"
            struct.pack_into("<I", data, offset, mapping[value])

    pos = header
    while pos < size:
        kind, head, length = struct.unpack_from("<HHI", data, pos)
        assert length >= head >= 8 and pos + length <= size
        if kind == 0x180:
            for offset in range(pos + head, pos + length, 4):
                replace(offset)
        elif kind == 0x102:
            start, width, count = struct.unpack_from("<HHH", data, pos + head + 8)
            assert width == 20
            for index in range(count):
                offset = pos + head + start + index * width
                if data[offset + 15] in (1, 2, 7, 8):
                    replace(offset + 16, offset + 15)
        elif kind == 0x104 and data[pos + head + 7] in (1, 2, 7, 8):
            replace(pos + head + 8, pos + head + 7)
        else:
            assert kind in (1, 0x100, 0x101, 0x103), hex(kind)
        pos += length
    assert pos == size
    return bytes(data)


def main() -> None:
    if DEST.exists():
        raise SystemExit(f"Refusing to overwrite {DEST}")
    with zipfile.ZipFile(ARCHIVE) as module:
        base_bytes = module.read("payload/Settings.apk")
    assert digest(base_bytes) == EXPECTED_BASE
    base_path = ROOT / "work/settings-global-polish-base.apk"
    base_path.write_bytes(base_bytes)

    current_ids = public_ids(CURRENT_RES)
    donor_ids = public_ids(DONOR_RES)
    mapping = {value: current_ids[key] for key, value in donor_ids.items() if key in current_ids}

    with zipfile.ZipFile(base_path) as base, zipfile.ZipFile(DONOR) as donor:
        avatar_colors = {
            donor_ids["color", "oos_usercenter_default_profile_out_bg_color"]: 0xFFC9DAE4,
            donor_ids["color", "usercenter_default_profile_bg_color"]: 0xFF000000,
        }
        avatar = remap_xml(donor.read("res/drawable/settings_usercenter_default_profile_ic.xml"), mapping, avatar_colors)
        search_avatar = remap_xml(donor.read("res/drawable/settings_search_usercenter_default_profile_ic.xml"), mapping, avatar_colors)
        oxygen_logo = remap_xml(donor.read("res/drawable/brand_logo.xml"), mapping)
        replacements = {
            "res/drawable/settings_usercenter_default_profile_ic.xml": avatar,
            "res/drawable/settings_search_usercenter_default_profile_ic.xml": search_avatar,
            "res/drawable/brand_logo.xml": oxygen_logo,
            # Current code selects this resource on 16.1-style builds; use the same OxygenOS logo.
            "res/drawable/brand_logo_16_1.xml": oxygen_logo,
        }
        # The OPD2403 global and current card backgrounds are already byte-identical.
        backgrounds = [n for n in donor.namelist() if "about_device_top_video_last_frame" in n]
        assert backgrounds and all(n in base.namelist() and donor.read(n) == base.read(n) for n in backgrounds)
        DEST.mkdir(parents=True)
        output = DEST / "Settings-global-avatar-oxygen-logo.apk"
        aligned_copy(base, output, replacements)

    with zipfile.ZipFile(base_path) as base, zipfile.ZipFile(output) as result:
        assert result.testzip() is None
        assert result.namelist() == base.namelist()
        changed = {n for n in base.namelist() if base.read(n) != result.read(n)}
        assert changed == set(replacements)
    (DEST / "changed-resources.txt").write_text("\n".join(sorted(replacements)) + "\n", encoding="utf-8")
    (DEST / "SHA256SUMS.txt").write_text(f"{digest(output.read_bytes())}  {output.name}\n", encoding="ascii")
    print(output)
    print("PASS: stable payload preserved except two global avatars and two OxygenOS logo targets")


if __name__ == "__main__":
    main()
