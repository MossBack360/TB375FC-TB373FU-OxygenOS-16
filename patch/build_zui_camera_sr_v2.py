"""Build the minimal ZUI Camera zoom-capture crash fix and Magisk module."""
from __future__ import annotations

import hashlib
import struct
import sys
import zlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "patch"))
from build_global_polish import aligned_copy  # noqa: E402


SOURCE = ROOT / "out/camera-crash-2026-09-10/ZuiCamera-installed.apk"
DEST = ROOT / "out/zui-camera-sr-runtime-fix-v2.0-2026-09-14"
EXPECTED_SOURCE = "6752402e1d1f2308941d50aaf056f9a69246337884f7cc1b9a7905b9f5f2c9ba"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class DexTables:
    def __init__(self, raw: bytes):
        self.data = bytearray(raw)
        string_count, string_off = struct.unpack_from("<II", self.data, 56)
        type_count, type_off = struct.unpack_from("<II", self.data, 64)
        proto_count, proto_off = struct.unpack_from("<II", self.data, 72)
        field_count, field_off = struct.unpack_from("<II", self.data, 80)
        method_count, method_off = struct.unpack_from("<II", self.data, 88)

        def read_uleb128(offset: int) -> tuple[int, int]:
            value = shift = 0
            while True:
                byte = self.data[offset]
                offset += 1
                value |= (byte & 0x7F) << shift
                if byte < 0x80:
                    return value, offset
                shift += 7

        self.strings: list[str] = []
        for index in range(string_count):
            offset = struct.unpack_from("<I", self.data, string_off + index * 4)[0]
            _, offset = read_uleb128(offset)
            end = self.data.index(0, offset)
            self.strings.append(bytes(self.data[offset:end]).decode("utf-8", "replace"))
        self.types = [
            self.strings[struct.unpack_from("<I", self.data, type_off + index * 4)[0]]
            for index in range(type_count)
        ]
        self.protos: list[str] = []
        for index in range(proto_count):
            _, return_idx, params_off = struct.unpack_from("<III", self.data, proto_off + index * 12)
            args: list[str] = []
            if params_off:
                size = struct.unpack_from("<I", self.data, params_off)[0]
                args = [
                    self.types[struct.unpack_from("<H", self.data, params_off + 4 + item * 2)[0]]
                    for item in range(size)
                ]
            self.protos.append(f"({''.join(args)}){self.types[return_idx]}")
        self.fields = []
        for index in range(field_count):
            class_idx, type_idx, name_idx = struct.unpack_from("<HHI", self.data, field_off + index * 8)
            self.fields.append((self.types[class_idx], self.strings[name_idx], self.types[type_idx]))
        self.methods = []
        for index in range(method_count):
            class_idx, proto_idx, name_idx = struct.unpack_from("<HHI", self.data, method_off + index * 8)
            self.methods.append((self.types[class_idx], self.strings[name_idx], self.protos[proto_idx]))

    def field(self, owner: str, name: str, desc: str) -> int:
        return self.fields.index((owner, name, desc))

    def method(self, owner: str, name: str, proto: str) -> int:
        return self.methods.index((owner, name, proto))

    def replace_once(self, old: bytes, new: bytes, label: str) -> int:
        assert len(old) == len(new), (label, len(old), len(new))
        count = self.data.count(old)
        assert count == 1, (label, count)
        position = self.data.index(old)
        self.data[position : position + len(old)] = new
        return position

    def finish(self, original: bytes, changed_ranges: list[tuple[int, int]]) -> bytes:
        self.data[12:32] = hashlib.sha1(self.data[32:]).digest()
        struct.pack_into("<I", self.data, 8, zlib.adler32(self.data[12:]) & 0xFFFFFFFF)
        changed = {index for index, pair in enumerate(zip(original, self.data)) if pair[0] != pair[1]}
        allowed = set(range(8, 32))
        for start, length in changed_ranges:
            allowed.update(range(start, start + length))
        assert changed <= allowed
        return bytes(self.data)


def invoke_35c(opcode: int, method: int, regs: list[int]) -> bytes:
    assert 0 <= len(regs) <= 5 and all(0 <= reg <= 15 for reg in regs)
    packed = regs + [0] * (5 - len(regs))
    c, d, e, f, g = packed
    return struct.pack("<BBHBB", opcode, (len(regs) << 4) | g, method, c | (d << 4), e | (f << 4))


def patch_classes(raw: bytes) -> bytes:
    dex = DexTables(raw)
    params = "Lcom/zui/camera/capture/AlgoController$Parameters;"
    controller = "Lcom/zui/camera/capture/AlgoController;"
    get_status = dex.method(params, "getMultiFrameStatus", "()[Z")
    get_support = dex.method(params, "getMultiFrameSupport", "()[Z")
    supports_field = dex.field(controller, "mMultiFrameAlgoSupports", "[Z")
    status_field = dex.field(controller, "mMultiFrameAlgoStatus", "[Z")

    # updateAlgoParams has one local, so p0=v1 and p1=v2.
    move_result_v0 = bytes((0x0C, 0x00))
    iput_supports = struct.pack("<BBH", 0x5B, 0x10, supports_field)
    iput_status = struct.pack("<BBH", 0x5B, 0x10, status_field)
    status_call = invoke_35c(0x6E, get_status, [2])
    support_call = invoke_35c(0x6E, get_support, [2])

    old = status_call + move_result_v0 + iput_supports + status_call + move_result_v0 + iput_status
    new = support_call + move_result_v0 + iput_supports + status_call + move_result_v0 + iput_status
    position = dex.replace_once(old, new, "AlgoController.updateAlgoParams support refresh")
    return dex.finish(raw, [(position, len(old))])


def write_module(apk: Path, module: Path, apk_hash: str) -> None:
    service = f'''#!/system/bin/sh
MODDIR=${{0%/*}}
resetprop debug.camera.morpho.sr.on 0
if [ "$1" != "--apply" ]; then
    until [ "$(getprop sys.boot_completed)" = "1" ]; do sleep 2; done
    sleep 8
    su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
    exit $?
fi
target=/system/priv-app/ZuiCamera/ZuiCamera.apk
payload="$MODDIR/payload/ZuiCamera.apk"
base={EXPECTED_SOURCE}
expected={apk_hash}
actual=$(sha256sum "$target")
[ "${{actual%% *}}" = "$base" ] || {{ echo 'Base APK mismatch; skipped'; exit 1; }}
[ -f "$payload" ] || exit 1
chmod 0644 "$payload" || exit 1
chcon u:object_r:system_file:s0 "$payload" || exit 1
mount --bind "$payload" "$target" || exit 1
resetprop debug.camera.morpho.sr.on 0
am force-stop com.zui.camera
mounted=$(sha256sum "$target")
[ "${{mounted%% *}}" = "$expected" ] || {{ umount "$target"; echo 'Bind verification failed'; exit 1; }}
echo "zui-camera-sr-v2=ok property=$(getprop debug.camera.morpho.sr.on)"
sha256sum "$target"
'''.encode("ascii")
    entries = {
        "module.prop": (
            "id=fixo_zui_camera_sr_disable\n"
            "name=FixO ZUI Camera Safe Capture\n"
            "version=2.0\n"
            "versionCode=2\n"
            "author=FixO\n"
            "description=Keeps Morpho SR disabled during runtime parameter refresh to prevent zoom-capture SIGILL.\n"
        ).encode("ascii"),
        "system.prop": b"debug.camera.morpho.sr.on=0\n",
        "service.sh": service,
        "payload/ZuiCamera.apk": apk.read_bytes(),
    }
    with ZipFile(module, "w") as archive:
        for name, content in entries.items():
            info = ZipInfo(name)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            archive.writestr(info, content)


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    assert digest(source_bytes) == EXPECTED_SOURCE
    DEST.mkdir(parents=True, exist_ok=True)
    output = DEST / "ZuiCamera-sr-runtime-fix-v2.apk"
    with ZipFile(SOURCE) as source:
        original_dex = source.read("classes.dex")
        replacements = {"classes.dex": patch_classes(original_dex)}
        aligned_copy(source, output, replacements)
        with ZipFile(output) as result:
            assert result.testzip() is None
            assert result.namelist() == source.namelist()
            changed = [name for name in source.namelist() if source.read(name) != result.read(name)]
            assert changed == ["classes.dex"], changed
            patched_dex = result.read("classes.dex")
            assert patched_dex != original_dex
            assert patched_dex[12:32] == hashlib.sha1(patched_dex[32:]).digest()
            assert struct.unpack_from("<I", patched_dex, 8)[0] == zlib.adler32(patched_dex[12:])

    apk_hash = digest(output.read_bytes())
    module = DEST / "fixo-zui-camera-sr-disable-v2.0-magisk.zip"
    write_module(output, module, apk_hash)
    with ZipFile(module) as archive:
        assert archive.testzip() is None
        assert digest(archive.read("payload/ZuiCamera.apk")) == apk_hash

    (DEST / "README.md").write_text(
        "# FixO ZUI Camera Safe Capture v2.0\n\n"
        "- Fixes `AlgoController.updateAlgoParams()` overwriting algorithm support with runtime status.\n"
        "- Keeps `debug.camera.morpho.sr.on=0`, so the incompatible Morpho HDSR path stays disabled.\n"
        "- Changes only `classes.dex`; native libraries, resources, and other algorithms are unchanged.\n"
        "- Uses a post-boot bind mount and can be reverted by disabling the module and rebooting.\n",
        encoding="utf-8",
    )
    (DEST / "SHA256SUMS.txt").write_text(
        f"{apk_hash}  {output.name}\n{digest(module.read_bytes())}  {module.name}\n",
        encoding="ascii",
    )
    print(f"APK={output}")
    print(f"APK_SHA256={apk_hash}")
    print(f"MODULE={module}")
    print(f"MODULE_SHA256={digest(module.read_bytes())}")


if __name__ == "__main__":
    main()
