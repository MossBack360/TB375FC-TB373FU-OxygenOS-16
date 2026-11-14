#!/system/bin/sh
# Temporary test: follow DRM DPMS only in off-mode charging.
[ "$(getprop ro.bootmode)" = charger ] || exit 0

(
    umask 077
    out=/data/adb/charger-backlight-trial
    node=/sys/class/leds/lcd-backlight/brightness
    dpms_node=/sys/class/drm/card0-DSI-1/dpms
    mkdir -p "$out" || exit 0
    saved=$(cat "$node" 2>/dev/null)
    case "$saved" in ''|*[!0-9]*) exit 0 ;; esac
    [ "$saved" -gt 0 ] || exit 0
    forced=0
    off_count=0
    i=0
    while [ "$i" -lt 180 ] && [ "$(getprop ro.bootmode)" = charger ]; do
        svc=$(getprop init.svc.charger)
        dpms=$(cat "$dpms_node" 2>/dev/null)
        brightness=$(cat "$node" 2>/dev/null)
        if [ "$svc" = running ] && [ "$dpms" = Off ]; then
            off_count=$((off_count + 1))
            if [ "$off_count" -ge 2 ] && [ "$forced" -eq 0 ] && [ "$brightness" -gt 0 ] 2>/dev/null; then
                echo 0 > "$node"
                forced=1
                echo "sample=$i action=blank dpms=$dpms before=$brightness after=$(cat "$node")" >> "$out/events.txt"
            fi
        else
            off_count=0
            if [ "$forced" -eq 1 ] && [ "$dpms" = On ]; then
                [ "$brightness" -gt 0 ] 2>/dev/null || echo "$saved" > "$node"
                forced=0
                echo "sample=$i action=unblank dpms=$dpms before=$brightness after=$(cat "$node")" >> "$out/events.txt"
            fi
        fi
        echo "sample=$i svc=$svc dpms=$dpms brightness=$(cat "$node" 2>/dev/null)" >> "$out/samples.txt"
        i=$((i + 1))
        sleep 1
    done
) </dev/null >/dev/null 2>&1 &
exit 0
