#!/system/bin/sh
# Linux key 0x00fc closes the cover; 0x00fd opens it.

until [ "$(getprop sys.boot_completed)" = 1 ]; do sleep 1; done

while true; do
    device=$(getevent -lp 2>/dev/null | awk '
        /^add device [0-9]+: \/dev\/input\/event[0-9]+/ { path=$4 }
        /name:[[:space:]]*"hall"/ { print path; exit }
    ')
    case "$device" in
        /dev/input/event[0-9]*) ;;
        *) sleep 5; continue ;;
    esac

    log -t XiaoxinHall "Listening on $device; switch=global.device_case_enabled"
    getevent -q "$device" | {
        last=
        while read -r type code value; do
            [ "$type" = 0001 ] && [ "$value" = 00000001 ] || continue
            case "$code" in
                00fc) state=closed; key=KEYCODE_SLEEP ;;
                00fd) state=open; key=KEYCODE_WAKEUP ;;
                *) continue ;;
            esac
            [ "$state" = "$last" ] && continue
            last=$state
            if [ "$(settings get global device_case_enabled 2>/dev/null)" != 1 ]; then
                log -t XiaoxinHall "$state ignored: Settings switch is off"
                continue
            fi
            if input keyevent "$key"; then
                log -t XiaoxinHall "$state -> $key"
            else
                last=
                log -t XiaoxinHall "Failed: $state -> $key"
            fi
        done
    }
    log -t XiaoxinHall 'Input reader stopped; reconnecting in 5 seconds'
    sleep 5
done
