#!/system/bin/sh
# Read-only, charger-mode kretprobe for the legacy DRM CRTC disable ioctl.
[ "$(getprop ro.bootmode)" = charger ] || exit 0

(
    umask 077
    out=/data/adb/charger-drm-return-probe-trial
    tr=/sys/kernel/tracing
    mkdir -p "$out" || exit 0
    [ -w "$tr/kprobe_events" ] || exit 0
    [ "$(cat "$tr/tracing_on")" = 0 ] || exit 0
    [ ! -s "$tr/kprobe_events" ] || exit 0

    if ! echo 'r:charger_setcrtc_ret drm_mode_setcrtc $retval' >> "$tr/kprobe_events" 2> "$out/registration-error.txt"; then
        cat "$tr/error_log" > "$out/kernel-error.txt" 2>/dev/null
        exit 0
    fi
    echo 1 > "$tr/events/kprobes/charger_setcrtc_ret/enable"
    echo 1 > "$tr/tracing_on"
    sleep 50
    cat "$tr/trace" > "$out/trace.txt"
    echo 0 > "$tr/tracing_on"
    echo 0 > "$tr/events/kprobes/charger_setcrtc_ret/enable"
    echo '-:charger_setcrtc_ret' >> "$tr/kprobe_events"
) </dev/null >/dev/null 2>&1 &
exit 0
