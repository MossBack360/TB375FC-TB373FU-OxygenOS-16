from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
BASE_XML = ROOT / "work/oxygen-current-dolby/audio_effects.xml"
DAX_APK = ROOT / "out/zui-17.5.10.057-stock-2026-09-08/daxService/daxService.apk"
OUT_DIR = ROOT / "out/dolby-dap-trial-2026-09-08"
ZIP_PATH = OUT_DIR / "fixo-dolby-dap-v1.1-magisk.zip"


def merged_audio_effects() -> bytes:
    text = BASE_XML.read_text(encoding="utf-8")
    library_anchor = '        <library name="oplus_audiox_legacy" path="liboplus_audiox_legacy.so"/>'
    effect_anchor = (
        '        <effect name="oplusaudiox" library="oplus_audiox_legacy" '
        'uuid="41f6c0f4-5d8f-11ec-bf63-0242ac130002"/>'
    )
    assert text.count(library_anchor) == 1
    assert text.count(effect_anchor) == 1
    text = text.replace(
        library_anchor,
        library_anchor
        + '\n        <library name="dap" path="libswdap.so"/>'
        + '\n        <library name="gamedap" path="libswgamedap.so"/>',
    )
    text = text.replace(
        effect_anchor,
        effect_anchor
        + '\n        <effect name="dap" library="dap" uuid="9d4921da-8225-4f29-aefa-39537a04bcaa"/>'
        + '\n        <effect name="gamedap" library="gamedap" uuid="3783c334-d3a0-4d13-874f-0032e5fb80e2"/>',
    )
    return text.encode("utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audio_xml = merged_audio_effects()
    module_prop = (
        "id=fixo_dolby_dap\n"
        "name=FixO Dolby DAP bridge (trial)\n"
        "version=1.1\n"
        "versionCode=2\n"
        "author=Codex for GY\n"
        "description=Registers the existing MT6897 Dolby DAP engine and restores ZUI DaxService.\n"
    ).encode()
    privapp_xml = b'''<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <privapp-permissions package="com.dolby.daxservice">
        <permission name="android.permission.INTERACT_ACROSS_USERS"/>
        <permission name="android.permission.INTERACT_ACROSS_USERS_FULL"/>
        <permission name="android.permission.MANAGE_USERS"/>
        <permission name="android.permission.WRITE_SECURE_SETTINGS"/>
        <permission name="android.permission.SUBSTITUTE_NOTIFICATION_APP_NAME"/>
    </privapp-permissions>
</permissions>
'''
    with ZipFile(ZIP_PATH, "w", ZIP_DEFLATED) as archive:
        archive.writestr("module.prop", module_prop)
        archive.writestr("system/vendor/etc/audio_effects.xml", audio_xml)
        archive.writestr(
            "system/system_ext/etc/permissions/privapp-permissions-fixo-daxservice.xml",
            privapp_xml,
        )
        archive.write(
            DAX_APK,
            "system/system_ext/priv-app/daxService/daxService.apk",
        )

    digest = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest().upper()
    (OUT_DIR / "SHA256SUMS.txt").write_text(
        f"{digest}  {ZIP_PATH.name}\n", encoding="ascii"
    )
    print(ZIP_PATH)
    print(digest)


if __name__ == "__main__":
    main()
