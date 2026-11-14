#!/system/bin/sh
# Temporary, read-only charger-mode trace. Remove after one reproduction.
[ "$(getprop ro.bootmode)" = charger ] || exit 0

(
    umask 077
    out=/data/adb/charger-offmode-trace
    mkdir -p "$out" || exit 0
    cat /proc/bootconfig > "$out/bootconfig.txt" 2>&1
    getprop > "$out/properties-start.txt" 2>&1
    dmesg -s 1048576 > "$out/kernel-start.txt" 2>&1
    /system/bin/dmesg -W > "$out/kernel-follow.txt" 2>&1 &
    follow_pid=$!
    sha256sum /system/bin/charger > "$out/charger-hash.txt" 2>&1

    i=0
    while [ "$i" -lt 90 ]; do
        {
            echo "sample=$i uptime=$(cat /proc/uptime 2>/dev/null)"
            echo "charger=$(getprop init.svc.charger)"
            echo "composer=$(getprop init.svc.vendor.hwcomposer-3-2)"
            echo "surfaceflinger=$(getprop init.svc.surfaceflinger)"
            echo "brightness=$(cat /sys/class/leds/lcd-backlight/brightness 2>/dev/null)"
            echo "dpms=$(cat /sys/class/drm/card0-DSI-1/dpms 2>/dev/null)"
            echo "charger_pid=$(pidof charger 2>/dev/null)"
        } >> "$out/samples.txt"
        case "$i" in
            15|35|60|89)
                dmesg -s 1048576 > "$out/kernel-$i.txt" 2>&1
                logcat -b all -d -t 2000 > "$out/logcat-$i.txt" 2>&1
                ;;
        esac
        i=$((i + 1))
        sleep 2
    done
    kill "$follow_pid" 2>/dev/null
) </dev/null >/dev/null 2>&1 &
exit 0
