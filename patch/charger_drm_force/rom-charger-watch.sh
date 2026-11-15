#!/system/bin/sh
# Charger-mode companion for the patched verbose charger binary.
[ "$(getprop ro.bootmode)" = charger ] || exit 0

helper=/system/bin/charger_drm_blank
panel=/sys/class/drm/card0-DSI-1/dpms

# Listen before the first charger animation ends. The key path also covers
# a charger animation-start message that arrives before the DRM device is ready.
(
    while :; do
        /system/bin/getevent -l | while IFS= read -r line; do
            case "$line" in
                *KEY_POWER*DOWN*)
                    sleep 0.2
                    pid=$(pidof charger)
                    case "$pid" in ''|*[!0-9]*) continue ;; esac
                    "$helper" wake "$pid" >/dev/null 2>&1
                    ;;
            esac
        done
        sleep 1
    done
) </dev/null >/dev/null 2>&1 &

while :; do
    /system/bin/dmesg -W | while IFS= read -r line; do
        case "$line" in
            *charger:*"animation starting"*)
                pid=$(pidof charger)
                case "$pid" in ''|*[!0-9]*) continue ;; esac
                "$helper" wake "$pid" >/dev/null 2>&1
                ;;
            *charger:*"animation done"*)
                [ "$(cat "$panel" 2>/dev/null)" = On ] || continue
                pid=$(pidof charger)
                case "$pid" in ''|*[!0-9]*) continue ;; esac
                "$helper" blank "$pid" >/dev/null 2>&1
                ;;
        esac
    done
    sleep 1
done
