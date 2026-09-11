"""Build an isolated SystemUI renderer trial for Material Contour Glow."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work/oxygen-launcher-current-2026-09-10/SystemUI-decoded"
BASE_APK = ROOT / "work/oxygen-launcher-current-2026-09-10/SystemUI.apk"
DEST = ROOT / "out/material-stroke-render-trial-2026-09-10"
WORK = SOURCE
PATCH_FILE = SOURCE / "smali_classes5/com/oplusos/systemui/common/blurability/platformblur/PlatformBlurDrawable.smali"
EXPECTED_BASE = "1a80578af3928915e91dee9d78a90f8286754a38ef942e24d24e2f84e694e906"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zip_write(path, entries):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            data = content.encode() if isinstance(content, str) else content
            info = zipfile.ZipInfo(name)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None


def main():
    assert SOURCE.is_dir() and BASE_APK.is_file()
    assert sha256(BASE_APK) == EXPECTED_BASE
    assert not DEST.exists(), f"Refusing to overwrite {DEST}"
    text = PATCH_FILE.read_text(encoding="utf-8")
    original_text = text
    needle = """    invoke-virtual {v0}, Landroid/graphics/drawable/Drawable;->invalidateSelf()V

    .line 291
    .line 292
    .line 293
"""
    assert text.count(needle) == 1
    injection = """    new-instance v1, Lcom/oplus/posteffect/GradientStrokeLineParams$LineParams;
    const/4 v2, 0x6
    const v3, 0x3ecccccd    # 0.4
    const v4, 0x3e6b851f    # 0.23
    const v5, 0x3e851eb8    # 0.26
    const/4 v6, 0x0
    const/4 v7, 0x0
    invoke-direct/range {v1 .. v7}, Lcom/oplus/posteffect/GradientStrokeLineParams$LineParams;-><init>(IFFFFF)V

    new-instance v6, Lcom/oplus/posteffect/GradientStrokeLineParams$LineParams;
    const/4 v7, 0x6
    const v8, 0x3e4ccccd    # 0.2
    const v9, 0x3e6b851f    # 0.23
    const v10, 0x3e851eb8    # 0.26
    const/4 v11, 0x0
    const/4 v12, 0x0
    invoke-direct/range {v6 .. v12}, Lcom/oplus/posteffect/GradientStrokeLineParams$LineParams;-><init>(IFFFFF)V

    new-instance v7, Lcom/oplus/posteffect/GradientStrokeLineParams;
    const/4 v8, -0x1
    const v9, 0x3f2e147b    # 0.68
    invoke-direct {v7, v8, v9, v1, v6}, Lcom/oplus/posteffect/GradientStrokeLineParams;-><init>(IFLcom/oplus/posteffect/GradientStrokeLineParams$LineParams;Lcom/oplus/posteffect/GradientStrokeLineParams$LineParams;)V
    invoke-virtual {v0, v7}, Lcom/oplus/posteffect/drawable/BaseDrawable;->setGradientStrokeLineParams(Lcom/oplus/posteffect/GradientStrokeLineParams;)V

    invoke-virtual {v0}, Landroid/graphics/drawable/Drawable;->invalidateSelf()V

    .line 291
    .line 292
    .line 293
"""
    PATCH_FILE.write_text(text.replace(needle, injection), encoding="utf-8", newline="\n")
    dex = WORK / "build/apk/classes5.dex"
    try:
        # Apktool 3.0.3 assembles dex files before it attempts to relink the
        # resources.  This SystemUI tree has private framework resources that
        # cannot be relinked on the host, so consume the freshly assembled
        # classes5.dex and keep every original APK resource byte-for-byte.
        result = subprocess.run(["java", "-jar", str(ROOT / "tools/apktool_3.0.3.jar"), "b", str(WORK), "-f"], check=False)
        assert dex.is_file() and dex.stat().st_size > 1_000_000, result.returncode
        patched_dex = dex.read_bytes()
    finally:
        PATCH_FILE.write_text(original_text, encoding="utf-8", newline="\n")

    readme = """# Material Contour Glow renderer trial

This independent trial patches only the current OxygenOS SystemUI renderer.
The current APK already contains the AGSL stroke shader primitives; this adds
gradient-stroke parameters at the platform-blur draw step, which is the
missing consumer path found by comparing ColorOS. It does not add or replace
the Settings switch.

It is deliberately bind-mounted after boot and checks the original SystemUI
SHA-256 before applying. If SystemUI does not remain alive after restart, the
service unmounts the payload and disables the module automatically.

This is a renderer trial, not a replacement for the archived Settings or
Launcher modules. Remove it from Magisk to return to the original renderer.
"""
    service = """#!/system/bin/sh
MODDIR=${0%/*}
if [ \"$1\" != \"--apply\" ]; then
    until [ \"$(getprop sys.boot_completed)\" = \"1\" ]; do sleep 2; done
    sleep 8
    su -mm -c \"sh '$MODDIR/service.sh' --apply\" >\"$MODDIR/runtime.log\" 2>&1
    exit $?
fi
target=/system_ext/priv-app/SystemUI/SystemUI.apk
payload=\"$MODDIR/payload/SystemUI.apk\"
expected=1a80578af3928915e91dee9d78a90f8286754a38ef942e24d24e2f84e694e906
actual=$(sha256sum \"$target\")
[ \"${actual%% *}\" = \"$expected\" ] || { echo 'Base SystemUI mismatch; skipped'; exit 1; }
[ -f \"$payload\" ] || exit 1
chmod 0644 \"$payload\" || exit 1
chcon u:object_r:system_file:s0 \"$payload\" || exit 1
mount --bind \"$payload\" \"$target\" || exit 1
for proc in $(pidof com.android.systemui); do kill \"$proc\"; done
sleep 15
first=$(pidof com.android.systemui)
sleep 15
second=$(pidof com.android.systemui)
if [ -z \"$first\" ] || [ \"$first\" != \"$second\" ]; then
    umount \"$target\"
    touch \"$MODDIR/disable\"
    for proc in $(pidof com.android.systemui); do kill \"$proc\"; done
    echo 'SystemUI unstable; restored original and disabled trial'
    exit 1
fi
echo \"material-stroke-render=ok pid=$second\"
sha256sum \"$target\"
"""
    module_prop = """id=fixo_material_stroke_render_trial
name=Material Contour Glow Renderer Trial
version=1.0
versionCode=1
author=local
    description=Adds the missing SystemUI gradient-stroke consumer path with rollback guard.
"""
    DEST.mkdir(parents=True)
    output = DEST / "fixo-material-stroke-render-trial-v1.0-magisk.zip"
    patched_apk = ROOT / "work/material-stroke-render-trial-SystemUI.apk"
    with zipfile.ZipFile(BASE_APK) as source_zip, zipfile.ZipFile(patched_apk, "w") as apk_zip:
        for info in source_zip.infolist():
            data = patched_dex if info.filename == "classes5.dex" else source_zip.read(info)
            apk_zip.writestr(info, data)
    with zipfile.ZipFile(patched_apk) as check:
        assert check.testzip() is None
    zip_write(output, {"module.prop": module_prop, "README.md": readme, "service.sh": service, "payload/SystemUI.apk": patched_apk.read_bytes()})
    (DEST / "SHA256SUMS.txt").write_text(f"{sha256(output)}  {output.name}\n{sha256(BASE_APK)}  base-SystemUI.apk\n{sha256(patched_apk)}  payload/SystemUI.apk\n", encoding="utf-8")
    patched_apk.unlink()
    print(output)
    PATCH_FILE.write_text(original_text, encoding="utf-8", newline="\n")
    print("PASS: apktool build and ZIP integrity checks passed")


if __name__ == "__main__":
    main()
