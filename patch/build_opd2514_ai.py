"""Build the safe OPD2514 international AI add-on module.

The target Oxygen image already contains AIUnit, AIWriter, Metis, DeepThinker
and AONService.  This module only adds the OPD2514 components absent from the
current image, so it does not replace the existing AI runtime.
"""
from pathlib import Path
import hashlib
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work/opd2514-a28-selected"
DEST = ROOT / "out/opd2514-ai-addons-2026-09-10-v1.1"


FILES = {
    "system/my_product/app/AIPaint/AIPaint.apk":
        SOURCE / "my_product/my_product/app/AIPaint/AIPaint.apk",
    "system/my_product/app/GoogleGemini/GoogleGemini.apk":
        SOURCE / "my_product/my_product/app/GoogleGemini/GoogleGemini.apk",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert SOURCE.exists(), SOURCE
    assert not DEST.exists(), f"Refusing to overwrite {DEST}"
    for target, source in FILES.items():
        assert source.is_file(), source

    DEST.mkdir(parents=True)
    zip_path = DEST / "fixo-opd2514-ai-addons-v1.1-magisk.zip"
    readme = """# OPD2514 international AI add-ons

This is an independent Magisk module for the current TB375FC/TB373FU
OxygenOS port. It adds the OPD2514 international packages that were absent
from the current image:

- `com.oplus.aipaint` (AIPaint / AI image functions)
- `com.google.android.apps.bard` (Google Gemini)

The current image already contains `com.oplus.aiunit`, `com.oplus.aiwriter`,
`com.oplus.metis`, `com.oplus.deepthinker`, and `com.aiunit.aon`; this module
does not replace them. The OPD2514 `appfeature.ai_front_apps.xml` is already
byte-identical to the current image and is therefore not duplicated.

The APKs are placed under the Magisk `system/my_product` overlay. A small
post-boot fallback also binds them to `/my_product` when that mount already
exposes the corresponding target path. This does not replace Settings, SystemUI,
Launcher, or UXDesign. If an AI page remains hidden, the next check is the
Settings feature gate and region policy, not another APK replacement.
"""
    (DEST / "README.md").write_text(readme, encoding="utf-8")

    module_prop = (
        "id=fixo_opd2514_ai_addons\n"
        "name=OPD2514 International AI Add-ons\n"
        "version=1.1\n"
        "versionCode=1\n"
        "author=local\n"
        "description=Adds OPD2514 AIPaint and Google Gemini without replacing the existing AI runtime.\n"
    )
    service = """#!/system/bin/sh
MODDIR=${0%/*}
apply_one() {
    target="$1"; payload="$2"
    [ -f "$target" ] && [ -f "$payload" ] || return 0
    chmod 0644 "$payload" || return 1
    chcon u:object_r:system_file:s0 "$payload" >/dev/null 2>&1 || true
    mount --bind "$payload" "$target" || return 1
    echo "bound $target"
}
if [ "$1" = "--apply" ]; then
    apply_one /my_product/app/AIPaint/AIPaint.apk "$MODDIR/system/my_product/app/AIPaint/AIPaint.apk"
    apply_one /my_product/app/GoogleGemini/GoogleGemini.apk "$MODDIR/system/my_product/app/GoogleGemini/GoogleGemini.apk"
    exit 0
fi
until [ "$(getprop sys.boot_completed)" = "1" ]; do sleep 1; done
su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
"""
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("module.prop", module_prop)
        archive.writestr("README.md", readme)
        info = zipfile.ZipInfo("service.sh")
        info.external_attr = 0o100755 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, service)
        for target, source in FILES.items():
            info = zipfile.ZipInfo(target)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, source.read_bytes())

    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {"module.prop", "README.md", "service.sh", *FILES}
        for target, source in FILES.items():
            assert archive.read(target) == source.read_bytes()

    sums = [f"{sha256(zip_path)}  {zip_path.name}"]
    for target, source in FILES.items():
        sums.append(f"{sha256(source)}  {target}")
    (DEST / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(zip_path)
    print("PASS: ZIP integrity and byte identity checks passed")


if __name__ == "__main__":
    main()
