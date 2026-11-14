#!/system/bin/sh
# Charger-only follow-up: defer and repeat the backlight-off write after the
# final frame has settled. This is an experiment, not a confirmed repair.
[ "$(getprop ro.bootmode)" = charger ] || exit 0

(
    umask 077
    out=/data/adb/charger-backlight-event-delay-trial
    node=/sys/class/leds/lcd-backlight/brightness
    hw=/sys/class/leds/lcd-backlight/mt_brightness_hw_changed
    mkdir -p "$out" || exit 0
    saved=$(cat "$node" 2>/dev/null)
    case "$saved" in ''|*[!0-9]*) exit 0 ;; esac
    [ "$saved" -gt 0 ] || exit 0
    echo "saved=$saved" > "$out/events.txt"
    /system/bin/dmesg -W | while IFS= read -r line; do
        case "$line" in
            *charger:*"animation done"*)
                # Keep the proven immediate write, then repeat after the
                # charger frame/DRM transaction has had time to finish.
                echo 0 > "$node"
                echo "done after=$(cat "$node") hw=$(cat "$hw" 2>/dev/null) line=$line" >> "$out/events.txt"
                (
                    sleep 1
                    if [ "$(cat "$node" 2>/dev/null)" = 0 ]; then
                        echo 0 > "$node"
                        echo "late-off after=$(cat "$node") hw=$(cat "$hw" 2>/dev/null)" >> "$out/events.txt"
                    fi
                ) &
                ;;
            *charger:*"animation starting"*)
                before=$(cat "$node" 2>/dev/null)
                [ "$before" -gt 0 ] 2>/dev/null || echo "$saved" > "$node"
                echo "start before=$before after=$(cat "$node") hw=$(cat "$hw" 2>/dev/null) line=$line" >> "$out/events.txt"
                ;;
        esac
    done
) </dev/null >/dev/null 2>&1 &
exit 0
