#!/system/bin/sh
MODDIR=${0%/*}
if [ "$1" != "--apply" ]; then
    until [ "$(getprop sys.boot_completed)" = "1" ]; do sleep 2; done
    sleep 8
    su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
    exit $?
fi
target=/system_ext/priv-app/SystemUI/SystemUI.apk
payload="$MODDIR/payload/SystemUI.apk"
expected=72cfa6810c72d7aef8cfdfd8f57ee8f88117c2b5867f272d3700a08fe3c32dc7
actual=$(sha256sum "$target")
[ "${actual%% *}" = "$expected" ] || { echo 'Base APK mismatch; skipped'; exit 1; }
[ -f "$payload" ] || exit 1
chmod 0644 "$payload" || exit 1
chcon u:object_r:system_file:s0 "$payload" || exit 1
mount --bind "$payload" "$target" || exit 1
for proc in $(pidof com.android.systemui); do kill "$proc"; done
sleep 15
first=$(pidof com.android.systemui)
sleep 15
second=$(pidof com.android.systemui)
if [ -z "$first" ] || [ "$first" != "$second" ]; then
    umount "$target"
    touch "$MODDIR/disable"
    for proc in $(pidof com.android.systemui); do kill "$proc"; done
    echo 'SystemUI unstable; restored original and disabled trial'
    exit 1
fi
echo "caption-overlay=ok pid=$second"
sha256sum "$target"
