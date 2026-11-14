"""Pack the unchanged v2.0 camera payload for an early PackageManager scan test."""

from hashlib import sha256
from pathlib import Path
import sys
from zipfile import ZIP_STORED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT.parent / "temp3/稳定安装/01-当前启用-Magisk/03-camera-sr-disable-config-v2.0.zip"
OUTDIR = ROOT / "out/zui-camera-early-scan-2026-11-14"
RAW_SHA = "42e55eb755521791ac757e6c8ca1d0b1c6b6fcdf02e7a29004a126fcface1676"
SIGBLOCK_SHA = "7a21a0c3f28b1eb715dbbb9bd4a1be5e3722eef4f998de100c68bd58a4beb862"


def main() -> None:
    candidate = sys.argv[1:] == ["--candidate"]
    if candidate:
        apk = (ROOT / "out/zui-camera-rom-scan-2026-11-13/ZuiCamera-v2-rom-signing-block-candidate.apk").read_bytes()
        expected = SIGBLOCK_SHA
        module_id = "fixo_zui_camera_sigblock_scan_trial"
        out = OUTDIR / "fixo-zui-camera-sigblock-scan-v0.1.zip"
    else:
        assert len(sys.argv) == 1, "usage: script.py [--candidate]"
        with ZipFile(ARCHIVE) as source:
            apk = source.read("payload/ZuiCamera.apk")
        expected = RAW_SHA
        module_id = "fixo_zui_camera_early_scan_trial"
        out = OUTDIR / "fixo-zui-camera-early-scan-v0.1.zip"
    assert sha256(apk).hexdigest() == expected
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", compression=ZIP_STORED) as trial:
        trial.writestr("module.prop", "\n".join((
            f"id={module_id}",
            "name=ZUI Camera Early Scan Trial",
            "version=0.1",
            "versionCode=1",
            "author=MossBack360",
            "description=Tests the v2.0 camera patch at PackageManager scan time.",
            "",
        )))
        trial.writestr("system.prop", "debug.camera.morpho.sr.on=0\n")
        trial.writestr("system/priv-app/ZuiCamera/ZuiCamera.apk", apk)
    with ZipFile(out) as trial:
        assert len(trial.namelist()) == 3
        assert all("\\" not in name for name in trial.namelist())
        assert sha256(trial.read("system/priv-app/ZuiCamera/ZuiCamera.apk")).hexdigest() == expected
    print(out)
    print(sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
