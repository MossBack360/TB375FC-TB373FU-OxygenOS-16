from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
BASE_XML = ROOT / "work/oxygen-current-dolby/audio_effects.xml"
DAX_APK = ROOT / "out/zui-17.5.10.057-stock-2026-09-08/daxService/daxService.apk"
ZUI_DAP_LIB = ROOT / "out/zui-17.5.10.057-stock-2026-09-08/vendor-dolby/libswdap.so"
OUT_DIR = ROOT / "out/dolby-dap-confirmed-2026-09-09"
ZIP_PATH = OUT_DIR / "fixo-dolby-dap-v1.5-zui-engine-magisk.zip"
MODULE_SRC = ROOT / "patch/dolby-dap-overlay"


def add(archive: ZipFile, name: str, data: bytes, mode: int = 0o100644) -> None:
    info = ZipInfo(name)
    info.external_attr = mode << 16
    archive.writestr(info, data, ZIP_DEFLATED)


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
        + '\n        <library name="dvl" path="libdlbvol.so"/>'
        + '\n        <library name="gamedap" path="libswgamedap.so"/>',
    )
    text = text.replace(
        effect_anchor,
        effect_anchor
        + '\n        <effect name="dap" library="dap" uuid="9d4921da-8225-4f29-aefa-39537a04bcaa"/>'
        + '\n        <effect name="dlb_music_listener" library="dvl" uuid="40f66c8b-5aa5-4345-8919-53ec431aaa98"/>'
        + '\n        <effect name="dlb_ring_listener" library="dvl" uuid="21d14087-558a-4f21-94a9-5002dce64bce"/>'
        + '\n        <effect name="dlb_alarm_listener" library="dvl" uuid="6aff229c-30c6-4cc8-9957-dbfe5c1bd7f6"/>'
        + '\n        <effect name="dlb_notification_listener" library="dvl" uuid="1f0091e3-6ad8-40fe-9b09-5948f9a26e7e"/>'
        + '\n        <effect name="gamedap" library="gamedap" uuid="3783c334-d3a0-4d13-874f-0032e5fb80e2"/>',
    )
    preprocess_anchor = '        <preprocess>'
    assert text.count(preprocess_anchor) == 1
    text = text.replace(
        preprocess_anchor,
        '        <postprocess>\n'
        '            <stream type="music">\n'
        '                <apply effect="dap"/>\n'
        '                <apply effect="dlb_music_listener"/>\n'
        '            </stream>\n'
        '        </postprocess>\n'
        + preprocess_anchor,
    )
    return text.encode("utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audio_xml = merged_audio_effects()
    module_prop = (
        "id=fixo_dolby_dap\n"
        "name=FixO Dolby DAP bridge\n"
        "version=1.5-zui-engine\n"
        "versionCode=6\n"
        "author=Codex for GY\n"
        "description=Restores the stock TB375FC MT6897 DAP engine and attaches it directly to music sessions.\n"
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
        add(archive, "module.prop", module_prop)
        add(archive, "README.md", (MODULE_SRC / "README.md").read_bytes())
        add(archive, "service.sh", (MODULE_SRC / "service.sh").read_bytes(), 0o100755)
        add(archive, "sepolicy.rule", (MODULE_SRC / "sepolicy.rule").read_bytes())
        add(archive, "system/vendor/etc/audio_effects.xml", audio_xml)
        add(
            archive,
            "system/system_ext/etc/permissions/privapp-permissions-fixo-daxservice.xml",
            privapp_xml,
        )
        archive.write(
            DAX_APK,
            "system/system_ext/priv-app/daxService/daxService.apk",
        )
        archive.write(
            ZUI_DAP_LIB,
            "system/vendor/lib64/soundfx/libswdap.so",
        )

    with ZipFile(ZIP_PATH) as archive:
        expected = {
            "module.prop",
            "README.md",
            "service.sh",
            "sepolicy.rule",
            "system/vendor/etc/audio_effects.xml",
            "system/system_ext/etc/permissions/privapp-permissions-fixo-daxservice.xml",
            "system/system_ext/priv-app/daxService/daxService.apk",
            "system/vendor/lib64/soundfx/libswdap.so",
        }
        assert set(archive.namelist()) == expected
        assert (archive.getinfo("service.sh").external_attr >> 16) & 0o777 == 0o755

    digest = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest().upper()
    sums = []
    for path in sorted(OUT_DIR.glob("*.zip")):
        sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest().upper()}  {path.name}")
    (OUT_DIR / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="ascii")
    print(ZIP_PATH)
    print(digest)


if __name__ == "__main__":
    main()
