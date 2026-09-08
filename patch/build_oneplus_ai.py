"""Build a separate OnePlus AI trial on top of the confirmed homepage icons."""
import copy
import difflib
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile
import xml.etree.ElementTree as ET

from build_oxygen_icons import ROOT, DONOR, CURRENT_RES, OXYGEN_RES, digest, public_ids, remap_xml

BASE = ROOT / 'out/oxygen-icons-confirmed-2026-09-06/Settings.apk'
EXPECTED = '233769bec202b251a47aa9124dfbaae62ec555b9969d8dce243c819482f62eac'
WORK = ROOT / 'work/oneplus-ai-assemble'
DEST = ROOT / 'out/oneplus-ai-trial-2026-09-06'
CLASS = Path('smali_classes2/com/oplus/settings/feature/homepage/TopLevelSmartServicePreferenceController.smali')


def main():
    assert digest(BASE) == EXPECTED
    assert not WORK.exists() and not DEST.exists(), 'Refusing to overwrite a previous build'
    with zipfile.ZipFile(BASE) as base:
        assert base.read('classes2.dex') == (ROOT / 'work/assemble/build/apk/classes2.dex').read_bytes()
    shutil.copytree(ROOT / 'work/assemble', WORK, ignore=shutil.ignore_patterns('build', 'dist'))
    original = (WORK / CLASS).read_text(encoding='utf-8')
    old, new = 'const-string p1, "OPPO"', 'const-string p1, "OnePlus"'
    assert original.count(old) == 1
    updated = original.replace(old, new)
    (WORK / CLASS).write_text(updated, encoding='utf-8', newline='\n')
    subprocess.run(['java', '-jar', str(ROOT / 'tools/apktool_3.0.3.jar'), 'b', str(WORK),
                    '-o', str(WORK / 'assembled.apk')], check=True)
    current_ids, donor_ids = public_ids(CURRENT_RES), public_ids(OXYGEN_RES)
    mapping = {value: current_ids[key] for key, value in donor_ids.items() if key in current_ids}
    # Reuse the former AI foreground resource, referenced only by the replaced AI icon.
    gradient = '$settings_system_breeno_ic__0'
    mapping[donor_ids['drawable', gradient]] = current_ids['drawable', 'settings_ai_foreground']
    with zipfile.ZipFile(DONOR) as donor:
        replacements = {
            'classes2.dex': (WORK / 'build/apk/classes2.dex').read_bytes(),
            'res/drawable/settings_system_breeno_ic.xml': remap_xml(donor.read('res/drawable/settings_system_breeno_ic.xml'), mapping),
            'res/drawable/settings_ai_foreground.xml': remap_xml(donor.read('res/drawable/' + gradient + '.xml'), mapping),
        }
    DEST.mkdir(parents=True)
    output = DEST / 'Settings-oneplus-ai.apk'
    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(output, 'w') as result:
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
    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(output) as result:
        assert result.testzip() is None
        assert result.namelist() == base.namelist()
        assert {n for n in base.namelist() if base.read(n) != result.read(n)} == set(replacements)
    assert digest(BASE) == EXPECTED
    (DEST / 'title-change.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True), updated.splitlines(True),
        fromfile=str(CLASS), tofile=str(CLASS))), encoding='utf-8')
    (DEST / 'SHA256SUMS.txt').write_text(f'{digest(output)}  {output.name}\n', encoding='utf-8')
    print(output)
    print('PASS: only AI icon, gradient resource and classes2.dex changed; confirmed archive unchanged.')


if __name__ == '__main__':
    main()
