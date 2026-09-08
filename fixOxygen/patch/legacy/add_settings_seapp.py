from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
src = ROOT / "extract/device/plat_seapp_contexts"
out = ROOT / "out/plat_seapp_contexts"
text = src.read_text(encoding="utf-8")
rule = "user=system isPrivApp=true name=com.android.settings domain=system_app type=system_app_data_file levelFrom=all\n"
if rule not in text:
    lines = text.splitlines(keepends=True)
    lines.insert(1, rule)
    text = "".join(lines)
out.write_text(text, encoding="utf-8", newline="\n")

module = ROOT / "out/oxygen-settings-fix-magisk.zip"
tmp = ROOT / "out/oxygen-settings-fix-magisk-with-seapp.zip"
with zipfile.ZipFile(module) as old, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as new:
    for entry in old.infolist():
        new.writestr(entry, old.read(entry))
    new.write(out, "system/etc/selinux/plat_seapp_contexts")
tmp.replace(module)
print(module)
