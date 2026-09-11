"""Build caption + original drag-corner fallback + back-gesture fix."""
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


SOURCE = ROOT / "out/fullscreen-caption-confirmed-2026-09-09/SystemUI-caption.apk"
DEST = ROOT / "out/systemui-gesture-polish-v0.5-2026-09-11"
EXPECTED_SOURCE = "1a80578af3928915e91dee9d78a90f8286754a38ef942e24d24e2f84e694e906"


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
        changed = {i for i, (before, after) in enumerate(zip(original, self.data)) if before != after}
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


def patch_classes2(raw: bytes) -> bytes:
    dex = DexTables(raw)
    spring = "Lcom/android/wm/shell/windowdecor/FullscreenTaskIndicatorManager$SpringDragManager;"
    manager = "Lcom/android/wm/shell/windowdecor/FullscreenTaskIndicatorManager;"
    image = "Lcom/android/wm/shell/windowdecor/FullscreenTaskImageView;"
    utils = "Lcom/android/wm/shell/fullscreen/OplusFlexibleWindowAnimationUtils;"

    context_field = dex.field(spring, "mContext", "Landroid/content/Context;")
    parent_field = dex.field(spring, "this$0", manager)
    get_display = dex.method("Landroid/content/Context;", "getDisplay", "()Landroid/view/Display;")
    get_display_radius = dex.method(utils, "getDisplayCornerRadius", "(Landroid/view/Display;)I")
    get_indicator = dex.method(manager, "-$$Nest$fgetmIndicatorView", f"({manager}){image}")
    get_fallback_radius = dex.method(image, "getCornerRadius", "()I")

    def iget_object(field: int) -> bytes:
        return struct.pack("<BBH", 0x54, 0x04, field)  # iget-object v4, v0

    old_fallback = (
        iget_object(context_field)
        + invoke_35c(0x6E, get_display, [4])
        + bytes((0x0C, 0x04))
        + invoke_35c(0x71, get_display_radius, [4])
        + bytes((0x0A, 0x04))
    )
    new_fallback = (
        iget_object(parent_field)
        + invoke_35c(0x71, get_indicator, [4])
        + bytes((0x0C, 0x04))
        + invoke_35c(0x6E, get_fallback_radius, [4])
        + bytes((0x0A, 0x04))
    )
    fallback_pos = dex.replace_once(old_fallback, new_fallback, "display-radius fallback")

    # Keep the confirmed v0.2 behavior: only restore the tablet's existing
    # fullscreen radius while dragging.  Do not alter the formal freeform
    # handoff or its stock corner-radius animation.
    return dex.finish(raw, [(fallback_pos, len(old_fallback))])


def patch_classes6(raw: bytes) -> bytes:
    dex = DexTables(raw)
    scrim = "Lcom/oplusos/systemui/common/util/ScrimUtil;"
    get_anim_level = dex.method(scrim, "getAnimLevel", "()I")

    # SideGestureNavView selects NonRubberBandBezierCalculator when the global
    # animation level is 3.  That calculator displays the fully extended side
    # handle from the first visible frame.  Fall through to the existing
    # RubberBandBezierCalculator at every level, without changing the global
    # animation setting used by the rest of SystemUI.
    prefix = (
        invoke_35c(0x71, get_anim_level, [])
        + bytes((0x0A, 0x00))       # move-result v0
        + bytes((0x12, 0x21))       # const/4 v1, 0x2
        + bytes((0x36, 0x10))       # if-gt v0, v1, +BBBB
    )
    count = dex.data.count(prefix)
    assert count == 1, ("side-gesture calculator selector", count)
    branch_pos = dex.data.index(prefix) + len(prefix) - 2
    old_branch = bytes(dex.data[branch_pos : branch_pos + 4])
    assert old_branch[:2] == bytes((0x36, 0x10))
    dex.data[branch_pos : branch_pos + 4] = bytes(4)  # two DEX nop instructions
    return dex.finish(raw, [(branch_pos, 4)])


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    assert digest(source_bytes) == EXPECTED_SOURCE
    DEST.mkdir(parents=True, exist_ok=True)
    output = DEST / "SystemUI-gesture-polish-v0.5.apk"
    with ZipFile(SOURCE) as source:
        replacements = {
            "classes2.dex": patch_classes2(source.read("classes2.dex")),
            "classes6.dex": patch_classes6(source.read("classes6.dex")),
        }
        aligned_copy(source, output, replacements)
        with ZipFile(output) as result:
            assert result.testzip() is None
            changed = [name for name in source.namelist() if source.read(name) != result.read(name)]
            assert changed == ["classes2.dex", "classes6.dex"], changed

    module = DEST / "fixo-systemui-gesture-polish-v0.5-magisk.zip"
    service = (ROOT / "out/fullscreen-caption-confirmed-2026-09-09/service.sh").read_bytes().replace(b"\r\n", b"\n")
    entries = {
        "module.prop": (
            "id=fixo_fullscreen_caption\n"
            "name=TB375FC OxygenOS SystemUI gesture polish\n"
            "version=0.5\n"
            "versionCode=5\n"
            "author=FixO\n"
            "description=Enable fullscreen caption controls, retain the original drag-corner fix, and restore follow-finger back gesture animation.\n"
        ).encode(),
        "service.sh": service,
        "payload/SystemUI.apk": output.read_bytes(),
    }
    with ZipFile(module, "w") as archive:
        for name, content in entries.items():
            info = ZipInfo(name)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            archive.writestr(info, content)

    (DEST / "README.md").write_text(
        "# OxygenOS SystemUI gesture polish v0.5\n\n"
        "- Keeps the confirmed fullscreen three-dot menu patch.\n"
        "- Uses the existing 30 px tablet fullscreen radius instead of the zero display-radius report.\n"
        "- Keeps the confirmed v0.2 drag-corner behavior; formal freeform handoff remains stock.\n"
        "- Forces the existing rubber-band back-gesture calculator instead of the level-3 instant-expanded calculator.\n"
        "- Keeps the global animation level unchanged.\n"
        "- Only `classes2.dex` and `classes6.dex` differ from the confirmed caption SystemUI.\n",
        encoding="utf-8",
    )
    (DEST / "SHA256SUMS.txt").write_text(
        f"{digest(output.read_bytes())}  {output.name}\n{digest(module.read_bytes())}  {module.name}\n",
        encoding="ascii",
    )
    print(output)
    print(module)


if __name__ == "__main__":
    main()
