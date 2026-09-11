#!/system/bin/sh

MODDIR=${0%/*}

if [ "$1" = "--apply" ]; then
    target=/system_ext/app/UXDesign/UXDesign.apk
    payload="$MODDIR/payload/UXDesign.apk"
    [ -f "$payload" ] && [ -f "$target" ] || exit 1
    chmod 0644 "$payload" || exit 1
    chcon u:object_r:system_file:s0 "$payload" >/dev/null 2>&1
    mount --bind "$payload" "$target" || exit 1
    am force-stop com.oplus.uxdesign >/dev/null 2>&1
    log -t FixOTexture "Applied contour glow trial UXDesign overlay"
    echo "material-stroke-overlay=ok"
    exit 0
fi

until [ "$(getprop sys.boot_completed)" = "1" ]; do
    sleep 1
done

su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
