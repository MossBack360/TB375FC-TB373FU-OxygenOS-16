"""Keep communication feature gates without forcing a Wi-Fi tablet's radio HAL."""

import hashlib
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "temp3/稳定安装/01-当前启用-Magisk/23-communication-sharing-backend-v0.9-unified-feature.zip"
OUT = ROOT / "out/virtualcomm-safe-trial-2026-11-16/fixo-virtualcomm-v1.0-no-forced-ril.zip"
SHA = "7ec62c0fc4018e8b9062077214045f7f3d51c203efa566e60ecb6748dbde3636"

SERVICE = b'''#!/system/bin/sh
MODDIR=${0%/*}
until [ "$(getprop sys.boot_completed)" = 1 ]; do sleep 2; done
# Leave SIM mode and virtual RIL under the stock connection lifecycle.
resetprop -n persist.vendor.radio.virtualcomm 1
resetprop -n persist.vendor.radio.virtualcomm.enable 1
sleep 5
{
    echo "multisim=$(getprop persist.radio.multisim.config)"
    echo "virtualcomm=$(getprop persist.vendor.radio.virtualcomm)"
    echo "virtual_ril_0=$(getprop init.svc.virtual-ril-daemon-0)"
    echo "virtual_ril_1=$(getprop init.svc.virtual-ril-daemon-1)"
    service check IVirtualComm
} >"$MODDIR/runtime.log" 2>&1
'''


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SHA
    with ZipFile(SOURCE) as source:
        post = source.read("post-fs-data.sh")
        start = post.index(b"# These two properties")
        end = post.index(b"# Merge into the feature table", start)
        post = post[:start] + post[end:]
        assert b"resetprop" not in post
        customize = source.read("customize.sh").replace(b'set_perm "$MODPATH/system.prop" 0 0 0644\n', b"")
        prop = source.read("module.prop").decode().replace("version=0.9-unified-feature", "version=1.0-no-forced-ril-trial").replace("versionCode=9", "versionCode=10")
        entries = {
            "module.prop": prop.encode(), "customize.sh": customize,
            "post-fs-data.sh": post, "service.sh": SERVICE,
        }
        for name in source.namelist():
            if name.startswith("system/") and not name.endswith("/"):
                entries[name] = source.read(name)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w") as archive:
        for name, data in entries.items():
            item = ZipInfo(name)
            item.compress_type = ZIP_DEFLATED
            item.external_attr = (0o100755 if name.endswith(".sh") else 0o100644) << 16
            archive.writestr(item, data)
    with ZipFile(OUT) as archive:
        assert archive.testzip() is None
        assert all("\\" not in name for name in archive.namelist())
    print(OUT, hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
