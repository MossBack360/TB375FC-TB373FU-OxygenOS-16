#!/system/bin/sh
# Off-mode charger only. Recover from the first animation's failed panel blank.
[ "$(getprop ro.bootmode)" = charger ] || exit 0
MODDIR=${0%/*}
(
    logdir=/data/adb/charger-drm-force
    mkdir -p "$logdir" || exit 0
    echo "watcher started bootmode=$(getprop ro.bootmode)" >> "$logdir/events.txt"
    # A physical Power press must be able to wake the display even if the
    # charger's animation-start log arrives too early or never arrives.
    (
        /system/bin/getevent -l /dev/input/event1 | while IFS= read -r keyline; do
            case "$keyline" in
                *KEY_POWER*DOWN*)
                    sleep 0.2
                    pid=$(pidof charger)
                    case "$pid" in ''|*[!0-9]*) continue ;; esac
                    echo "power=$keyline pid=$pid" >> "$logdir/events.txt"
                    "$MODDIR/system/bin/charger_drm_blank" wake "$pid" >> "$logdir/events.txt" 2>&1
                    ;;
            esac
        done
    ) </dev/null >/dev/null 2>&1 &
    /system/bin/dmesg -W | while IFS= read -r line; do
        case "$line" in
            *charger:*"animation starting"*)
                pid=$(pidof charger)
                case "$pid" in ''|*[!0-9]*) continue ;; esac
                echo "wake event=$line pid=$pid" >> "$logdir/events.txt"
                "$MODDIR/system/bin/charger_drm_blank" wake "$pid" >> "$logdir/events.txt" 2>&1
                echo "wake status=$? after=$(cat /sys/class/drm/card0-DSI-1/dpms 2>/dev/null)" >> "$logdir/events.txt"
                ;;
            *charger:*"animation done"*)
                before=$(cat /sys/class/drm/card0-DSI-1/dpms 2>/dev/null)
                [ "$before" = On ] || continue
                pid=$(pidof charger)
                case "$pid" in ''|*[!0-9]*) continue ;; esac
                echo "event=$line before=$before pid=$pid" >> "$logdir/events.txt"
                "$MODDIR/system/bin/charger_drm_blank" blank "$pid" >> "$logdir/events.txt" 2>&1
                echo "status=$? after=$(cat /sys/class/drm/card0-DSI-1/dpms 2>/dev/null)" >> "$logdir/events.txt"
                ;;
        esac
    done
) </dev/null >/dev/null 2>&1 &
exit 0
