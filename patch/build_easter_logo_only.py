"""Restore complete stable animations; replace only the separate easter egg logo."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
from build_global_polish import aligned_copy

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'out/settings-easter-logo-only-2026-09-08'
BASE = ROOT / 'out/settings-blue-red-card-confirmed-2026-09-08/fixo-settings-blue-red-card-magisk.zip'

def main():
    DEST.mkdir(parents=True, exist_ok=False)
    with ZipFile(BASE) as module:
        stable = module.read('payload/Settings.apk')
        assert hashlib.sha256(stable).hexdigest() == '7ecad47e76a810bfe385e012633adb4fa1fd3be16e5aab45a9af4b660f9e94a9'
        import io
        apk = DEST / 'Settings-easter-oxygen-logo.apk'
        target = 'res/drawable/about_device_easter_egg_logo.xml'
        with ZipFile(io.BytesIO(stable)) as base:
            aligned_copy(base, apk, {target: base.read('res/drawable/brand_logo.xml')})
            with ZipFile(apk) as result:
                assert result.testzip() is None
                assert {n for n in base.namelist() if base.read(n) != result.read(n)} == {target}
        output = DEST / 'fixo-settings-easter-logo-only-magisk.zip'
        with ZipFile(output, 'w') as result:
            for entry in module.infolist():
                data = module.read(entry)
                if entry.filename == 'payload/Settings.apk':
                    data = apk.read_bytes()
                elif entry.filename == 'module.prop':
                    data = b'id=fixo_settings_confirmed\nname=Settings - OxygenOS card and easter egg logo\nversion=3.6\nversionCode=9\nauthor=local\ndescription=Full original animation, blue-red card, international OxygenOS easter egg logo.\n'
                result.writestr(entry, data)
    (DEST / 'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in (apk, output)), encoding='ascii')
    print((DEST / 'SHA256SUMS.txt').read_text())

if __name__ == '__main__':
    main()
