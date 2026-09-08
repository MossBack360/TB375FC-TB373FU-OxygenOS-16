"""Preserve signed boot-time APK, then overlay the confirmed Settings after boot."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'out/settings-boot-recovery-2026-09-07'


def main():
    original = (ROOT / 'extract/Settings.apk').read_bytes()
    fixed = (ROOT / 'out/oneplus-ai-confirmed-2026-09-06/Settings.apk').read_bytes()
    assert hashlib.sha256(original).hexdigest() == '7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12'
    assert hashlib.sha256(fixed).hexdigest() == '268d650808b6a7b23061f298d54549787dabe69ca6f1ef99e3072e85abccbf97'
    service = (ROOT / 'patch/settings-postboot-service.sh').read_bytes().replace(b'\r\n', b'\n')
    assert b'\r' not in service
    entries = {
        'module.prop': b'id=fixo_settings_confirmed\nname=Confirmed Settings - signed boot and postboot overlay\nversion=3.2\nversionCode=5\nauthor=local\ndescription=Original signed APK at boot; confirmed Oxygen icons and OnePlus AI overlay after boot.\n',
        'service.sh': service,
        'system/system_ext/priv-app/Settings/Settings.apk': original,
        'payload/Settings.apk': fixed,
    }
    DEST.mkdir(exist_ok=True)
    output = DEST / 'fixo-settings-postboot-v2-magisk.zip'
    assert not output.exists(), 'Refusing to overwrite an existing package'
    with zipfile.ZipFile(output, 'w') as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(name)
            info.external_attr = (0o100755 if name == 'service.sh' else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for name, data in entries.items():
            assert archive.read(name) == data
    (DEST / 'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
        for p in sorted(DEST.glob('*.zip'))), encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
