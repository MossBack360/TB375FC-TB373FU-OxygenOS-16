"""Build the independent OplusGestureUI MTK tilt-value compatibility module."""
from pathlib import Path
import hashlib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "work/oxygen-gesture-current-2026-09-10/OplusGestureUI.apk"
DEX = ROOT / "work/lift-to-wake-gestureui-2026-09-10/decoded-nores/build/apk/classes.dex"
DEST = ROOT / "out/lift-to-wake-sensor-2026-09-10"

BASE_SHA256 = "49a04980b912d04eb8198e55fc772e1cf4081a6a362bf3826bc583093d1d7f16"
DEX_SHA256 = "752ad6fad99911545a6c6d7b89f52b07130d8c52572762f37bc7f07d3b69903b"


def sha256(path: Path) -> str:
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def replace_dex(output: Path) -> None:
    dex = DEX.read_bytes()
    with zipfile.ZipFile(BASE) as source, zipfile.ZipFile(output, "w") as target:
        for item in source.infolist():
            target.writestr(item, dex if item.filename == "classes.dex" else source.read(item.filename))

    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(output) as patched:
        assert patched.testzip() is None
        assert base.namelist() == patched.namelist()
        changed = [name for name in base.namelist() if base.read(name) != patched.read(name)]
        assert changed == ["classes.dex"], changed
        assert hashlib.sha256(patched.read("classes.dex")).hexdigest() == DEX_SHA256


def package_module(payload: Path, output: Path) -> None:
    service = (ROOT / "patch/gestureui-postboot-service.sh").read_bytes().replace(b"\r\n", b"\n")
    prop = (
        "id=fixo_lift_to_wake_sensor\n"
        "name=TB375FC OxygenOS Lift to wake sensor compatibility\n"
        "version=1.0\n"
        "versionCode=1\n"
        "author=MossBack360\n"
        "description=Maps the standard MTK tilt detector value to OPlus native raise-to-wake.\n"
    ).encode("utf-8")
    readme = (
        "# TB375FC OxygenOS 抬起亮屏传感器兼容补丁\n\n"
        "本机 MTK TYPE_TILT_DETECTOR 按 Android 标准在检测到倾斜时上报 1.0，"
        "OPlus 原机服务却只在收到 0.0 时唤醒，并在收到 1.0 时注销监听。\n\n"
        "本模块只交换 OplusGestureUI 对 0.0/1.0 的处理：1.0 调用系统原生 "
        "OplusPowerManager.wakeUp，0.0 保留为取消事件。它使用硬件唤醒传感器，"
        "不轮询加速度计。需搭配 Settings 3.7 或手动启用"
        " oplus_customize_gesture_wake_up_arouse。\n"
    ).encode("utf-8")
    entries = {
        "module.prop": prop,
        "README.md": readme,
        "service.sh": service,
        "system/system_ext/app/OplusGestureUI/OplusGestureUI.apk": BASE.read_bytes(),
        "payload/OplusGestureUI.apk": payload.read_bytes(),
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
    assert sha256(DEX) == DEX_SHA256
    DEST.mkdir(parents=True, exist_ok=True)
    payload = DEST / "OplusGestureUI-lift-to-wake.apk"
    module = DEST / "fixo-lift-to-wake-sensor-v1.0-magisk.zip"
    replace_dex(payload)
    package_module(payload, module)
    (DEST / "README.md").write_bytes(zipfile.ZipFile(module).read("README.md"))
    (DEST / "SHA256SUMS.txt").write_text(
        f"{sha256(payload)}  {payload.name}\n{sha256(module)}  {module.name}\n",
        encoding="utf-8",
    )
    print(module)
    print("Payload SHA256:", sha256(payload))


if __name__ == "__main__":
    main()
