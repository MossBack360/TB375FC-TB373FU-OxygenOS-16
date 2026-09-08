"""Copy homepage vectors, remapping binary XML references to the fixed APK's IDs."""
import copy
import hashlib
from pathlib import Path
import shutil
import struct
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'out/confirmed-2026-09-06/Settings.apk'
DONOR = ROOT / 'extract/opd2403 oxygen os settings/Settings.apk'
DEST = ROOT / 'out/oxygen-icons-trial-2026-09-06'
CURRENT_RES = ROOT / 'work/icons-current/res'
OXYGEN_RES = ROOT / 'work/icons-oxygen/res'
EXPECTED = '6d92c4dc3e3d7b169c57592e673eb4077a6f9fd503fe7fba7608ec771af8ebce'
ANDROID = '{http://schemas.android.com/apk/res/android}'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_ids(res):
    return {(e.attrib['type'], e.attrib['name']): int(e.attrib['id'], 16)
            for e in ET.parse(res / 'values/public.xml').getroot()}


def remap_xml(raw, mapping):
    data = bytearray(raw)
    kind, header, size = struct.unpack_from('<HHI', data)
    assert kind == 3 and size == len(data)

    def replace(offset):
        value = struct.unpack_from('<I', data, offset)[0]
        if value >> 24 == 0x7f:
            assert value in mapping, f'Unmapped resource: {value:#x}'
            struct.pack_into('<I', data, offset, mapping[value])

    pos = header
    while pos < size:
        kind, head, length = struct.unpack_from('<HHI', data, pos)
        assert length >= head >= 8 and pos + length <= size
        if kind == 0x180:  # XML resource map
            for offset in range(pos + head, pos + length, 4):
                replace(offset)
        elif kind == 0x102:  # XML start element / typed attributes
            start, width, count = struct.unpack_from('<HHH', data, pos + head + 8)
            assert width == 20
            for index in range(count):
                offset = pos + head + start + index * width
                assert offset + width <= pos + length
                if data[offset + 15] in (1, 2, 7, 8):
                    replace(offset + 16)
        elif kind == 0x104:  # CDATA typed value
            if data[pos + head + 7] in (1, 2, 7, 8):
                replace(pos + head + 8)
        else:
            assert kind in (1, 0x100, 0x101, 0x103), hex(kind)
        pos += length
    assert pos == size
    return bytes(data)


def main():
    assert digest(BASE) == EXPECTED
    if DEST.exists():
        raise SystemExit(f'Refusing to overwrite {DEST}')
    current_ids, donor_ids = public_ids(CURRENT_RES), public_ids(OXYGEN_RES)
    mapping = {value: current_ids[key] for key, value in donor_ids.items() if key in current_ids}
    menus = [{e.get(ANDROID + 'key'): e.get(ANDROID + 'icon')
              for e in ET.parse(res / 'xml/top_level_settings_oplus.xml').iter()
              if e.get(ANDROID + 'icon')} for res in (CURRENT_RES, OXYGEN_RES)]
    selected = {value.split('/')[-1] for key, value in menus[0].items()
                if menus[1].get(key) == value and key != 'usercenter_preference'
                and value != '@drawable/settings_system_breeno_ic'}
    pending = [p for p in OXYGEN_RES.glob('drawable*/*.xml') if p.stem in selected]
    replacements = {}
    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(DONOR) as donor:
        while pending:
            path = pending.pop()
            relative = path.relative_to(OXYGEN_RES)
            existing = CURRENT_RES / relative
            if existing.exists() and existing.read_bytes() == path.read_bytes():
                continue
            # Apktool normalizes redundant directory qualifiers; resolve original ZIP path.
            folder = relative.parent.name
            matches = [n for n in donor.namelist() if n.startswith('res/' + folder)
                       and Path(n).name == path.name
                       and (Path(n).parent.name == folder or Path(n).parent.name.startswith(folder + '-v'))]
            assert len(matches) == 1, (relative, matches)
            name = matches[0]
            if name in replacements:
                continue
            assert name in base.namelist(), f'Missing destination resource {name}'
            replacements[name] = remap_xml(donor.read(name), mapping)
            for element in ET.parse(path).iter():
                for value in element.attrib.values():
                    if value.startswith('@drawable/'):
                        dependency = value.split('/', 1)[1]
                        assert ('drawable', dependency) in current_ids
                        pending.extend(OXYGEN_RES.glob('drawable*/' + dependency + '.xml'))
        assert 'res/drawable/settings_wifi_ic.xml' in replacements
        assert 'res/drawable/settings_about_device_ic.xml' in replacements
        DEST.mkdir(parents=True)
        shutil.copyfile(BASE, DEST / 'Settings-before-icons.apk')
        output = DEST / 'Settings-oxygen-icons.apk'
        with zipfile.ZipFile(output, 'w') as result:
            for entry in base.infolist():
                info = copy.copy(entry)
                info.extra = b''
                if info.compress_type == zipfile.ZIP_STORED:
                    alignment = 16384 if info.filename.startswith('lib/') and info.filename.endswith('.so') else 4
                    offset = result.fp.tell() + 30 + len(info.filename.encode())
                    if offset % alignment:
                        padding = (-offset - 4) % alignment
                        info.extra = struct.pack('<HH', 0xffff, padding) + bytes(padding)
                result.writestr(info, replacements.get(entry.filename, base.read(entry)))
        with zipfile.ZipFile(output) as result:
            assert result.testzip() is None
            assert result.namelist() == base.namelist()
            changed = {n for n in result.namelist() if result.read(n) != base.read(n)}
            assert changed == set(replacements)
    assert digest(BASE) == digest(DEST / 'Settings-before-icons.apk') == EXPECTED
    (DEST / 'changed-resources.txt').write_text('\n'.join(sorted(replacements)) + '\n', encoding='utf-8')
    (DEST / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in
                                             (DEST / 'Settings-before-icons.apk', output)), encoding='utf-8')
    print(f'Built {output}; replaced {len(replacements)} XML files; all other entries unchanged.')


if __name__ == '__main__':
    main()
