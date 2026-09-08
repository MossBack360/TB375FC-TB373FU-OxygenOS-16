"""Apply the clone-profile API compatibility fix to an apktool decode."""
from pathlib import Path
import difflib
import hashlib

ROOT = Path(__file__).resolve().parent.parent
APK = ROOT / "extract/Settings.apk"
BASE = ROOT / "work/settings/smali_classes2/com/oplus/settings"
FILES = [
    "feature/appmanager/AppManagerUtils.smali",
    "feature/notification/oaid/OAIDPreload.smali",
    "privacy/OplusNotificationAccessSettings.smali",
    "feature/display/compatible/FoldDatabaseHelper.smali",
    "feature/display/applandscapemode/AppLandscapeManager.smali",
]
OLD = "Lcom/oplus/multiapp/OplusMultiAppManager;->getMultiAppUserInfoList()Ljava/util/List;"
NEW = "Lcom/oplus/settings/feature/appmanager/AppManagerUtils;->getMultiAppUserInfoList(Lcom/oplus/multiapp/OplusMultiAppManager;)Ljava/util/List;"


def main():
    changes = []
    for name in FILES:
        path = BASE / name
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        hits = [i for i, line in enumerate(lines) if OLD in line]
        if len(hits) != 1:
            raise SystemExit(f"Expected one original call in {name}; use a fresh decode")
        index = hits[0]
        assert "invoke-virtual {" in lines[index]
        lines[index] = lines[index].replace("invoke-virtual", "invoke-static").replace(OLD, NEW)
        modified = "".join(lines)
        if name == FILES[0]:
            modified += "\n" + (ROOT / "patch/getMultiAppUserInfoList.smali").read_text(encoding="utf-8")
        changes.append((path, original, modified))

    diff = []
    for path, original, modified in changes:
        name = path.relative_to(ROOT).as_posix()
        diff.extend(difflib.unified_diff(original.splitlines(True), modified.splitlines(True),
                                        fromfile="a/" + name, tofile="b/" + name))
        path.write_text(modified, encoding="utf-8", newline="\n")
    (ROOT / "patch/settings-compat.patch").write_text("".join(diff), encoding="utf-8", newline="\n")
    print("Patched 5 callers; added one shared compatibility method")
    print("Input SHA256:", hashlib.sha256(APK.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
