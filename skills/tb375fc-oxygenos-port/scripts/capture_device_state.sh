#!/system/bin/sh

echo "DEVICE"
echo "captured_at=$(date -Iseconds 2>/dev/null || date)"
echo "model=$(getprop ro.product.model)"
echo "device=$(getprop ro.product.device)"
echo "product=$(getprop ro.build.product)"
echo "fingerprint=$(getprop ro.build.fingerprint)"
echo "release=$(getprop ro.build.version.release)"
echo "sdk=$(getprop ro.build.version.sdk)"
echo "boot_completed=$(getprop sys.boot_completed)"
echo "anim_level=$(getprop persist.sys.oplus.anim_level)"
echo "upgrade_anim_level=$(getprop persist.sys.oplus.upgrade_anim_level)"
echo "systemui_pid=$(pidof com.android.systemui)"
echo
echo "MODULES"
for d in /data/adb/modules/*; do
    [ -d "$d" ] || continue
    echo "--- ${d##*/} ---"
    [ -f "$d/disable" ] && echo "status=DISABLED" || echo "status=ACTIVE"
    [ -f "$d/remove" ] && echo "remove=PENDING"
    [ -f "$d/module.prop" ] && cat "$d/module.prop"
done
