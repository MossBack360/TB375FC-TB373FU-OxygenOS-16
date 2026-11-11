"""Build a reversible SystemUI v0.5 trial with a fixed drag-preview radius."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import struct
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "out/systemui-gesture-polish-v0.5-2026-09-11/SystemUI-gesture-polish-v0.5.apk"
EXPECTED_SOURCE = "92c57e647c9520cb043be1d0a0cf010c6f1e7dec2b72129837b45cc261e57560"
BUILDER = ROOT / "out/systemui-gesture-polish-v0.5-2026-09-11/build_systemui_gesture_v05.py"

spec = importlib.util.spec_from_file_location("old_systemui_builder", BUILDER)
assert spec and spec.loader
old_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old_builder)
from build_global_polish import aligned_copy  # noqa: E402


def patch_dex(raw: bytes, radius_px: int) -> bytes:
    dex = old_builder.DexTables(raw)
    spring = "Lcom/android/wm/shell/windowdecor/FullscreenTaskIndicatorManager$SpringDragManager;"
    manager = "Lcom/android/wm/shell/windowdecor/FullscreenTaskIndicatorManager;"
    image = "Lcom/android/wm/shell/windowdecor/FullscreenTaskImageView;"
    parent = dex.field(spring, "this$0", manager)
    indicator = dex.method(manager, "-$$Nest$fgetmIndicatorView", f"({manager}){image}")
    corner = dex.method(image, "getCornerRadius", "()I")
    old = (
        struct.pack("<BBH", 0x54, 0x04, parent)  # iget-object v4, v0, this$0
        + old_builder.invoke_35c(0x71, indicator, [4])
        + bytes((0x0C, 0x04))  # move-result-object v4
        + old_builder.invoke_35c(0x6E, corner, [4])
        + bytes((0x0A, 0x04))  # move-result v4
    )
    new = struct.pack("<BBH", 0x13, 0x04, radius_px) + bytes(len(old) - 4)
    position = dex.replace_once(old, new, "drag preview radius")
    return dex.finish(raw, [(position, len(old))])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("radius_px", type=int, help="drag preview radius in pixels, 0..200")
    args = parser.parse_args()
    if not 0 <= args.radius_px <= 200:
        parser.error("radius_px must be between 0 and 200")

    source = SOURCE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == EXPECTED_SOURCE
    out = ROOT / f"out/systemui-drag-radius-v0.6-{args.radius_px}px-test-2026-11-11"
    out.mkdir(parents=True, exist_ok=True)
    apk = out / f"SystemUI-drag-radius-{args.radius_px}px.apk"
    with ZipFile(SOURCE) as original:
        aligned_copy(original, apk, {"classes2.dex": patch_dex(original.read("classes2.dex"), args.radius_px)})
        with ZipFile(apk) as result:
            assert result.testzip() is None
            changed = [name for name in original.namelist() if original.read(name) != result.read(name)]
            assert changed == ["classes2.dex"], changed

    prop = (
        "id=fixo_fullscreen_caption\n"
        "name=TB375FC SystemUI drag radius trial\n"
        f"version=0.6-{args.radius_px}px-test\n"
        "versionCode=6\n"
        "author=MossBack360\n"
        f"description=Keep SystemUI v0.5 and trial a {args.radius_px}px bottom-corner drag preview radius.\n"
    ).encode()
    service = (ROOT / "patch/fullscreen-caption/service.sh").read_bytes().replace(b"\r\n", b"\n")
    module = out / f"fixo-systemui-drag-radius-{args.radius_px}px-v0.6-test.zip"
    with ZipFile(module, "w") as archive:
        for name, contents in {
            "module.prop": prop,
            "service.sh": service,
            "payload/SystemUI.apk": apk.read_bytes(),
        }.items():
            entry = ZipInfo(name)
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            archive.writestr(entry, contents)
    with ZipFile(module) as check:
        assert all("\\" not in name for name in check.namelist())
        assert check.testzip() is None
    print(apk, hashlib.sha256(apk.read_bytes()).hexdigest())
    print(module, hashlib.sha256(module.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
