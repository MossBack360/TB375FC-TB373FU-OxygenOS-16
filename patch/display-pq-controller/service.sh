#!/system/bin/sh

MODDIR=${0%/*}
CTL="$MODDIR/pqctl.jar"
LAST_AUTO=
LAST_MODE=
LAST_PQ_PID=

message() {
    log -t FixODisplayPQ "$*"
}

run_ctl() {
    env CLASSPATH="$CTL:/system_ext/framework/mediatek-framework.jar" \
        app_process /system/bin com.fixo.displaypq.PqCtl "$@"
}

apply_auto() {
    case "$1" in
        0|1)
            if result=$(run_ctl chameleon "$1" 2>&1); then
                message "adaptive=$1 result=$result"
            else
                message "adaptive=$1 failed: $result"
                return 1
            fi
            ;;
    esac
}

apply_mode() {
    case "$1" in
        0) preset=1; label=vivid ;;
        1) preset=2; label=natural ;;
        6) preset=0; label=professional ;;
        *) return 0 ;;
    esac
    if result=$(run_ctl preset "$preset" 2>&1); then
        message "mode=$1 ($label) preset=$preset result=$result"
    else
        message "mode=$1 ($label) failed: $result"
        return 1
    fi
}

while [ "$(getprop sys.boot_completed)" != 1 ]; do
    sleep 2
done

while :; do
    pq_pid=$(pidof vendor.mediatek.hardware.pq_aidl-service 2>/dev/null)
    if [ -n "$pq_pid" ] && [ "$pq_pid" != "$LAST_PQ_PID" ]; then
        LAST_PQ_PID=$pq_pid
        LAST_AUTO=
        LAST_MODE=
        message "PQ service pid=$pq_pid"
    fi

    auto=$(settings get system setting_enable_color_temperature_regulation 2>/dev/null)
    if [ "$auto" != "$LAST_AUTO" ]; then
        apply_auto "$auto" && LAST_AUTO=$auto
    fi

    mode=$(settings get secure oplus_customize_color_mode 2>/dev/null)
    if [ "$mode" != "$LAST_MODE" ]; then
        apply_mode "$mode" && LAST_MODE=$mode
    fi
    sleep 2
done
