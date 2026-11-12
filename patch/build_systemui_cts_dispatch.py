"""Trial: route the existing Home-bar long press to Android Contextual Search."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "out/cts-native-v0.1-2026-11-12/SystemUI-source.apk"
DECODED = ROOT / "work/systemui-cts-current-2026-11-12"
OUT = ROOT / "out/cts-native-v0.1-2026-11-12"
APKTOOL = ROOT / "tools/apktool_3.0.3.jar"
EXPECTED = "d5ecf22aa1c6fc3945a508c008af06554e3a1e6bcda9380258a9b266f821bf26"
SMALI = DECODED / "smali_classes6/com/oplus/systemui/navigationbar/ocrscreen/OplusOcrScreenBusiness.smali"

METHOD = """.method public final onLongPressed()V
    .locals 2

    :try_start_0
    iget-object v0, p0, Lcom/oplus/systemui/navigationbar/ocrscreen/OplusOcrScreenBusiness;->context:Landroid/content/Context;
    const-class v1, Landroid/app/contextualsearch/ContextualSearchManager;
    invoke-virtual {v0, v1}, Landroid/content/Context;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/app/contextualsearch/ContextualSearchManager;
    if-eqz v0, :fallback
    const/4 v1, 0x2
    invoke-virtual {v0, v1}, Landroid/app/contextualsearch/ContextualSearchManager;->startContextualSearch(I)V
    :try_end_0
    return-void

    :catch_0
    move-exception v0
    :fallback
    iget-object v0, p0, Lcom/oplus/systemui/navigationbar/ocrscreen/OplusOcrScreenBusiness;->currentServiceHandler:Lcom/oplus/systemui/navigationbar/ocrscreen/OplusOcrScreenServiceHandler;
    if-eqz v0, :done
    invoke-virtual {v0}, Lcom/oplus/systemui/navigationbar/ocrscreen/OplusOcrScreenServiceHandler;->onLongPressed()V
    :done
    return-void

    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0
.end method"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    assert sha(SOURCE.read_bytes()) == EXPECTED
    text = SMALI.read_text(encoding="utf-8")
    begin = text.index(".method public final onLongPressed()V")
    end = text.index(".end method", begin) + len(".end method")
    old = text[begin:end]
    assert "currentServiceHandler" in old and "ContextualSearchManager" not in old
    SMALI.write_text(text[:begin] + METHOD + text[end:], encoding="utf-8")

    rebuilt = OUT / "SystemUI-apktool-rebuilt.apk"
    subprocess.run(["java", "-Xmx6g", "-jar", str(APKTOOL), "b", str(DECODED), "-o", str(rebuilt)], check=True)
    final = OUT / "SystemUI-cts-dispatch-v0.1.apk"
    sys.path.insert(0, str(ROOT / "patch"))
    from build_global_polish import aligned_copy
    with ZipFile(SOURCE) as base, ZipFile(rebuilt) as built:
        patched_dex = built.read("classes6.dex")
        assert sha(patched_dex) != sha(base.read("classes6.dex"))
        aligned_copy(base, final, {"classes6.dex": patched_dex})
        with ZipFile(final) as checked:
            assert checked.testzip() is None
            changed = [n for n in base.namelist() if base.read(n) != checked.read(n)]
            assert changed == ["classes6.dex"], changed

    old_module = ROOT / "out/systemui-drag-radius-v0.6-26px-confirmed-2026-11-12/fixo-systemui-drag-radius-26px-v0.6.zip"
    with ZipFile(old_module) as archive:
        service = archive.read("service.sh")
    props = ("id=fixo_fullscreen_caption\n"
             "name=TB375FC SystemUI fixes and CTS trial\n"
             "version=0.7-cts-trial\nversionCode=8\nauthor=MossBack360\n"
             "description=Preserves confirmed SystemUI fixes; routes Home-bar long press to Contextual Search.\n").encode()
    module = OUT / "fixo-systemui-cts-dispatch-v0.7-test.zip"
    with ZipFile(module, "w") as archive:
        for name, data in {"module.prop": props, "service.sh": service, "payload/SystemUI.apk": final.read_bytes()}.items():
            entry = ZipInfo(name)
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            archive.writestr(entry, data)
    with ZipFile(module) as checked:
        assert checked.testzip() is None
        assert checked.namelist() == ["module.prop", "service.sh", "payload/SystemUI.apk"]
        assert all("\\" not in name for name in checked.namelist())
    print(final, sha(final.read_bytes()))
    print(module, sha(module.read_bytes()))


if __name__ == "__main__":
    main()
