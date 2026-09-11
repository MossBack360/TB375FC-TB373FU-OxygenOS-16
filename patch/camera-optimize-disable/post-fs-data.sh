#!/system/bin/sh
MODDIR=${0%/*}
mount --bind "$MODDIR/system_ext/etc/sys_camera_optimize_config.xml" /system_ext/etc/sys_camera_optimize_config.xml
