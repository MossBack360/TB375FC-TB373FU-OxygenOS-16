#!/system/bin/sh

LOG=/data/local/tmp/fixo_speaker_rotation.log
last=

until [ "$(getprop sys.boot_completed)" = "1" ]; do
    sleep 2
done

while true; do
    rotation=$(dumpsys window displays 2>/dev/null | sed -n 's/^[[:space:]]*mRotation=\([0-3]\).*/\1/p' | head -n 1)
    case "$rotation" in
        0) degrees=270 ;;
        1) degrees=0 ;;
        2) degrees=90 ;;
        3) degrees=180 ;;
        *) sleep 2; continue ;;
    esac

    /system_ext/bin/AudioSetParam -s "gsensor_rotation=$degrees"
    if [ "$degrees" != "$last" ]; then
        echo "$(date '+%F %T') rotation=$rotation gsensor_rotation=$degrees" >> "$LOG"
        last=$degrees
    fi
    sleep 2
done
