"""Remove only OPD2203 from the current SystemUI caption exclusion list."""
from pathlib import Path
import hashlib
import struct
import zlib
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from build_global_polish import aligned_copy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'work/oxygen-ui-current-2026-09-09/SystemUI.apk'
OUT = ROOT / 'out/fullscreen-caption-trial-2026-09-09'
EXPECTED = '72cfa6810c72d7aef8cfdfd8f57ee8f88117c2b5867f272d3700a08fe3c32dc7'


def patch_dex(raw):
    data = bytearray(raw)
    count, offset = struct.unpack_from('<II', data, 56)
    strings = {}
    for index in range(count):
        pos = struct.unpack_from('<I', data, offset + index * 4)[0]
        while data[pos] & 128:
            pos += 1
        pos += 1
        value = bytes(data[pos:data.index(0, pos)])
        if value in (b'OPD2202', b'OPD2203', b'OPD2405', b'OPD2408'):
            strings[value.decode()] = index
    assert len(strings) == 4
    # These consecutive const-string instructions are unique to the verified
    # FullscreenTaskWindowDecorController.<clinit> exclusion array.
    def instruction(register, name):
        return bytes((0x1a, register)) + struct.pack('<H', strings[name])
    old = instruction(2, 'OPD2202') + instruction(3, 'OPD2203') + instruction(4, 'OPD2405')
    new = instruction(2, 'OPD2202') + instruction(3, 'OPD2408') + instruction(4, 'OPD2405')
    assert data.count(old) == 1
    pos = data.index(old)
    data[pos:pos + len(old)] = new
    data[12:32] = hashlib.sha1(data[32:]).digest()
    struct.pack_into('<I', data, 8, zlib.adler32(data[12:]) & 0xffffffff)
    assert len(data) == len(raw)
    assert all(a == b for i, (a, b) in enumerate(zip(raw, data))
               if not (8 <= i < 32 or pos + 6 <= i < pos + 8))
    return bytes(data)


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'SystemUI-caption.apk'
    with ZipFile(SOURCE) as source:
        dex = patch_dex(source.read('classes2.dex'))
        aligned_copy(source, output, {'classes2.dex': dex})
        with ZipFile(output) as result:
            assert result.testzip() is None
            assert [n for n in source.namelist() if source.read(n) != result.read(n)] == ['classes2.dex']
    service = (ROOT / 'patch/fullscreen-caption/service.sh').read_bytes().replace(b'\r\n', b'\n')
    module = OUT / 'fixo-fullscreen-caption-v0.1-magisk.zip'
    entries = {
        'module.prop': b'id=fixo_fullscreen_caption\nname=TB375FC OxygenOS fullscreen caption\nversion=0.1-trial\nversionCode=1\nauthor=FixO\ndescription=Enable the fullscreen window menu on the verified OPD2203-based TB375FC port.\n',
        'service.sh': service,
        'payload/SystemUI.apk': output.read_bytes(),
    }
    with ZipFile(module, 'w') as archive:
        for name, content in entries.items():
            info = ZipInfo(name)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o100755 if name.endswith('.sh') else 0o100644) << 16
            archive.writestr(info, content)
    (OUT / 'SHA256SUMS.txt').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in (output, module)), encoding='ascii')
    print(module)


if __name__ == '__main__':
    main()
