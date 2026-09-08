from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
APKTOOL = ROOT / "tools/apktool_3.0.3.jar"


def files(root, suffix):
    if root.is_file():
        return [root] if root.match(suffix) else []
    return list(root.rglob(suffix))


def insert_before_all(path, needle, line):
    text = path.read_text(encoding="utf-8")
    old = text.splitlines()
    out = []
    changed = 0
    for current in old:
        if needle in current and (not out or out[-1].strip() != line):
            out.append("    " + line)
            changed += 1
        out.append(current)
    if changed:
        path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    return changed


def replace_result_after(path, needle, value):
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = 0
    for i, line in enumerate(lines):
        if needle in line:
            for j in range(i + 1, min(i + 7, len(lines))):
                if lines[j].strip().startswith("move-result"):
                    reg = lines[j].strip().split()[-1]
                    lines[j] = f"    const/4 {reg}, 0x{value}"
                    changed += 1
                    break
    if changed:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return changed


def force_boolean_methods(root, names, value):
    changed = 0
    for path in files(root, "*.smali"):
        lines = path.read_text(encoding="utf-8").splitlines()
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.lstrip().startswith(".method") and any(name in line for name in names) and line.rstrip().endswith(")Z"):
                j = i + 1
                while j < len(lines) and not lines[j].lstrip().startswith(".end method"):
                    j += 1
                if j < len(lines):
                    directive = next((x for x in lines[i + 1:j] if x.strip().startswith((".locals", ".registers"))), "    .locals 1")
                    out.extend([line, directive, f"    const/4 v0, 0x{value}", "    return v0", ".end method"])
                    i = j + 1
                    changed += 1
                    continue
            out.append(line)
            i += 1
        if changed and out != lines:
            path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    return changed


def force_int_methods(root, name, value):
    changed = 0
    for path in files(root, "*.smali"):
        lines = path.read_text(encoding="utf-8").splitlines()
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.lstrip().startswith(".method") and name in line and line.rstrip().endswith(")I"):
                j = i + 1
                while j < len(lines) and not lines[j].lstrip().startswith(".end method"):
                    j += 1
                directive = next((x for x in lines[i + 1:j] if x.strip().startswith((".locals", ".registers"))), "    .locals 1")
                out.extend([line, directive, f"    const/4 v0, 0x{value}", "    return v0", ".end method"])
                i = j + 1
                changed += 1
                continue
            out.append(line)
            i += 1
        if out != lines:
            path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    return changed


def main():
    out = ROOT / "work/sig-bypass"
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "work/device-framework", out / "framework")
    shutil.copytree(ROOT / "work/device-services", out / "services")
    fw = out / "framework"
    svc = out / "services"

    # Android 16 PackageParser / signing verifier compatibility changes.
    pp = next(fw.rglob("android/content/pm/PackageParser.smali"))
    insert_before_all(pp, "ApkSignatureVerifier;->unsafeGetCertsWithoutVerification", "const/4 v1, 0x1")
    ppe = next(fw.rglob("android/content/pm/PackageParser$PackageParserException.smali"))
    insert_before_all(ppe, "iput p1, p0, Landroid/content/pm/PackageParser$PackageParserException;->error:I", "const/4 p1, 0x0")
    for path in files(fw, "*SigningDetails.smali"):
        force_boolean_methods(path, ["checkCapability", "checkCapabilityRecover", "hasAncestorOrSelf"], "1")
    for path in files(fw, "*.smali"):
        if path.name in ("ApkSignatureSchemeV2Verifier.smali", "ApkSignatureSchemeV3Verifier.smali"):
            replace_result_after(path, "Ljava/security/MessageDigest;->isEqual([B[B)Z", "1")
        elif path.name == "ApkSigningBlockUtils.smali":
            replace_result_after(path, "Ljava/security/MessageDigest;->isEqual([B[B)Z", "1")
        elif path.name == "ApkSignatureVerifier.smali":
            force_int_methods(path, "getMinimumSignatureSchemeVersionForTargetSdk", "0")
            insert_before_all(path, "ApkSignatureVerifier;->verifyV1Signature", "const p3, 0x0")
    # PackageManager service uses SigningDetails capability checks during updates.
    for path in files(svc, "*.smali"):
        if path.name in ("PackageManagerServiceUtils.smali", "PackageManagerService$PackageManagerInternalImpl.smali", "InstallPackageHelper.smali", "PackageSessionVerifier.smali", "ReconcilePackageUtils.smali"):
            # Redirect the result of each capability check to true while preserving its register.
            for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
                pass
            replace_result_after(path, "SigningDetails;->checkCapability", "1")
            replace_result_after(path, "SigningDetails;->checkCapabilityRecover", "1")
    print("prepared", out)


if __name__ == "__main__":
    main()
