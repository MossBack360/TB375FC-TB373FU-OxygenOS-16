"""Prepare original OTA as privileged app and preserve the confirmed temporary fixes."""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'out/ota-system-restore-2026-09-07'
ADB = ROOT.parent / 'fixOxygen/platform-tools/adb.exe'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_module(path, module_prop, entries):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('module.prop', module_prop)
        for name, content in entries.items():
            info = zipfile.ZipInfo(name)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        for name, content in entries.items():
            assert archive.read(name) == content


def main():
    assert not DEST.exists(), 'Refusing to overwrite existing output'
    ota = ROOT / 'out/about-device-ota-trial-2026-09-07/OTA-original-oxygen.apk'
    settings = ROOT / 'out/oneplus-ai-confirmed-2026-09-06/Settings.apk'
    hall = ROOT / 'out/hall-confirmed-2026-09-06/xiaoxin-hall-confirmed-magisk.zip'
    assert digest(ota) == 'c71b111b3298e303658f1513879f4fa41432c54c24d9d498b79bb1df0ef64e8f'
    assert digest(settings) == '268d650808b6a7b23061f298d54549787dabe69ca6f1ef99e3072e85abccbf97'
    assert digest(hall) == '4da6ec07e6764566fbf536d0a06b4268b597f3f9b31e5fd6e3ed34b3171da313'
    dump = subprocess.check_output([str(ADB), 'shell', 'dumpsys', 'package', 'permissions'],
                                   text=True, encoding='utf-8', errors='replace')
    protections = {m.group(1): m.group(2) for m in re.finditer(
        r'Permission \[([^]]+)\].*?\n\s+sourcePackage=.*?\n\s+uid=.*? prot=([^\r\n]+)', dump)}
    manifest = ET.parse(ROOT / 'work/ota-resources/AndroidManifest.xml').getroot()
    requested = {e.get('{http://schemas.android.com/apk/res/android}name')
                 for e in manifest.findall('uses-permission')}
    privileged = sorted(n for n in requested if n.startswith('android.permission.')
                        and 'privileged' in protections.get(n, ''))
    assert 'android.permission.MANAGE_USERS' in privileged
    permissions = ET.Element('permissions')
    app = ET.SubElement(permissions, 'privapp-permissions', package='com.oplus.ota')
    # The task is restoring the page, not granting firmware installation/reboot capabilities.
    deny = {'android.permission.REBOOT', 'android.permission.RECOVERY',
            'android.permission.ACCESS_CACHE_FILESYSTEM'}
    for name in privileged:
        ET.SubElement(app, 'deny-permission' if name in deny else 'permission', name=name)
    ET.indent(permissions)
    xml = ET.tostring(permissions, encoding='utf-8', xml_declaration=True) + b'\n'
    DEST.mkdir()
    (DEST / 'privapp-permissions-fixo-ota.xml').write_bytes(xml)
    write_module(DEST / 'fixo-ota-system-magisk.zip',
        'id=fixo_ota_system\nname=Oxygen OTA page system permissions\nversion=1.0\nversionCode=1\nauthor=local\n'
        'description=Original Oxygen OTA with system permissions for its settings page.\n', {
            'system/system_ext/priv-app/FixOOTA/OTA.apk': ota.read_bytes(),
            'system/system_ext/etc/permissions/privapp-permissions-fixo-ota.xml': xml,
        })
    write_module(DEST / 'fixo-settings-oneplus-ai-magisk.zip',
        'id=fixo_settings_confirmed\nname=Confirmed Settings with Oxygen icons and OnePlus AI\n'
        'version=3.0\nversionCode=3\nauthor=local\ndescription=Preserves the user-confirmed Settings APK across reboot.\n', {
            'system/system_ext/priv-app/Settings/Settings.apk': settings.read_bytes(),
        })
    shutil.copyfile(hall, DEST / hall.name)
    (DEST / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n'
        for p in sorted(DEST.iterdir()) if p.is_file()), encoding='utf-8')
    print(DEST)
    print('PASS: APKs and existing hall module are byte-identical to archived inputs; ZIP verification passed.')


if __name__ == '__main__':
    main()
