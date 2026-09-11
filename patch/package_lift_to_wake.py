"""Patch the stable Settings payload so AOSP Lift to wake uses OPlus' native key."""
from pathlib import Path
import hashlib
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "out/settings-easter-logo-only-2026-09-08/Settings-easter-oxygen-logo.apk"
ORIGINAL = ROOT / "extract/Settings.apk"
DEX = ROOT / "work/lift-to-wake-trial-2026-09-10/dex/classes5.dex"
DEST = ROOT / "out/lift-to-wake-2026-09-10"

BASE_SHA256 = "76b66e842a6b19a7824bd5abe608d74b2bccf0d875b46515642625f8f3998ffe"
ORIGINAL_SHA256 = "7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12"
DEX_SHA256 = "d9dba664acdac011b9361c68e2f1e6265c254433d2cd0b76e811a56754035bda"


def sha256(path: Path) -> str:
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def replace_dex(output: Path) -> None:
    dex = DEX.read_bytes()
    assert b"oplus_customize_gesture_wake_up_arouse" in dex
    with zipfile.ZipFile(BASE, "r") as source, zipfile.ZipFile(output, "w") as target:
        for item in source.infolist():
            data = dex if item.filename == "classes5.dex" else source.read(item.filename)
            target.writestr(item, data)

    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(output) as patched:
        assert patched.testzip() is None
        assert base.namelist() == patched.namelist()
        changed = [name for name in base.namelist() if base.read(name) != patched.read(name)]
        assert changed == ["classes5.dex"], changed
        assert hashlib.sha256(patched.read("classes5.dex")).hexdigest() == DEX_SHA256


def package_module(payload: Path, output: Path) -> None:
    service = (ROOT / "patch/settings-postboot-service.sh").read_bytes().replace(b"\r\n", b"\n")
    readme = (
        "# 抬起亮屏兼容补丁\n\n"
        "用于 TB375FC/TB373FU OxygenOS 16。关闭系统优化后显示的 AOSP“Lift to wake”开关，"
        "原本写入被 OPlus 层屏蔽的 wake_gesture_enabled，导致开关立即回弹。\n\n"
        "本补丁让该开关控制系统原生 OPlus 抬起亮屏键 "
        "oplus_customize_gesture_wake_up_arouse；OplusGestureUI 会据此注册 MTK tilt 传感器。\n\n"
        "模块沿用稳定 Settings 的签名扫描后挂载方案，并完整保留此前的 Settings 图标、"
        "OxygenOS 系统卡片及彩带动画修复。\n"
    ).encode("utf-8")
    prop = (
        "id=fixo_settings_confirmed\n"
        "name=OxygenOS Settings and Lift to wake\n"
        "version=3.7\n"
        "versionCode=10\n"
        "author=MossBack360\n"
        "description=Stable Settings fixes plus native OPlus raise-to-wake switch compatibility.\n"
    ).encode("utf-8")
    entries = {
        "module.prop": prop,
        "README.md": readme,
        "service.sh": service,
        "system/system_ext/priv-app/Settings/Settings.apk": ORIGINAL.read_bytes(),
        "payload/Settings.apk": payload.read_bytes(),
    }
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(name)
            info.external_attr = (0o100755 if name == "service.sh" else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for name, data in entries.items():
            assert archive.read(name) == data


def main() -> None:
    assert sha256(BASE) == BASE_SHA256
    assert sha256(ORIGINAL) == ORIGINAL_SHA256
    assert sha256(DEX) == DEX_SHA256
    DEST.mkdir(parents=True, exist_ok=True)
    payload = DEST / "Settings-lift-to-wake.apk"
    module = DEST / "fixo-settings-lift-to-wake-v3.7-magisk.zip"
    replace_dex(payload)
    package_module(payload, module)
    (DEST / "README.md").write_bytes(zipfile.ZipFile(module).read("README.md"))
    files = [payload, module]
    (DEST / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in files), encoding="utf-8"
    )
    print(module)
    print("Payload SHA256:", sha256(payload))


if __name__ == "__main__":
    main()
