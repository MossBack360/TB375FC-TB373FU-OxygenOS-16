# Gallery-only module v1.1

- Archive: `E:\工程\github\xiaoxin Oxygen\temp3\稳定安装\07-待固化\02-global-apps-gallery-v1.1-gallery-only.zip`
- SHA-256: `866A67D5E9D40A3450707681EF85759DAB95EBB5C88F3CDB3AE256F473BFCF86`
- Module ID remains `fixo_global_apps`, version 1.1 / versionCode 2, so it upgrades the existing v1.0 instead of competing with it.
- Contains only `payload/OppoGallery2.apk`; the Gallery APK is byte-identical to v1.0, SHA-256 `5BE668588F05E182D4164693BA7AFFE7658B394833CE2445CBEAB5DE529229AD`.
- `service.sh` only bind-mounts `/my_stock/priv-app/OppoGallery2/OppoGallery2.apk`. The UserCenter payload, bind mount, and force-stop were removed. The old v1.0 archive remains untouched in `01-当前启用-Magisk`.
- Source: `patch/global-gallery-overlay/` and `patch/package_global_gallery.py`.
- Verified ZIP integrity, forward-slash entry names, exact payload list, matching Gallery hash, and `sh -n`. Per owner request, not installed on the device.

For ROM solidification, this is a Gallery-only input; do not carry over the v1.0 UserCenter replacement.
