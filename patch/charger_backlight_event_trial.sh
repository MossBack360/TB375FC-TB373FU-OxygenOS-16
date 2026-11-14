#!/system/bin/sh
# Temporary event-based charger backlight repair trial.
[ "$(getprop ro.bootmode)" = charger ] || exit 0

(
    umask 077
    out=/data/adb/charger-backlight-event-trial
    node=/sys/class/leds/lcd-backlight/brightness
    mkdir -p "$out" || exit 0
    saved=$(cat "$node" 2>/dev/null)
    case "$saved" in ''|*[!0-9]*) exit 0 ;; esac
    [ "$saved" -gt 0 ] || exit 0
    echo "saved=$saved" > "$out/events.txt"
    /system/bin/dmesg -W | while IFS= read -r line; do
        case "$line" in
            *charger:*"animation done"*)
                before=$(cat "$node" 2>/dev/null)
                echo 0 > "$node"
                echo "done before=$before after=$(cat "$node" 2>/dev/null) line=$line" >> "$out/events.txt"
                ;;
            *charger:*"animation starting"*)
                before=$(cat "$node" 2>/dev/null)
                [ "$before" -gt 0 ] 2>/dev/null || echo "$saved" > "$node"
                echo "start before=$before after=$(cat "$node" 2>/dev/null) line=$line" >> "$out/events.txt"
                ;;
            *charger:*)
                echo "$line" >> "$out/charger-kmsg.txt"
                ;;
        esac
    done
) </dev/null >/dev/null 2>&1 &
exit 0
