#!/system/bin/sh
# Read-only uprobe on the charger's statically linked DRM atomic AddProperty.
[ "$(getprop ro.bootmode)" = charger ] || exit 0

(
    umask 077
    out=/data/adb/charger-drm-property-probe-trial
    tr=/sys/kernel/tracing
    mkdir -p "$out" || exit 0
    [ -w "$tr/uprobe_events" ] || exit 0
    [ "$(cat "$tr/tracing_on")" = 0 ] || exit 0
    [ ! -s "$tr/uprobe_events" ] || exit 0

    # AArch64 drmModeAtomicAddProperty(req, object_id, property_id, value).
    echo 'p:charger_addprop /system/bin/charger:0x27910 obj=%x1 prop=%x2 value=%x3' >> "$tr/uprobe_events" || exit 0
    echo 1 > "$tr/events/uprobes/charger_addprop/enable"
    echo 1 > "$tr/tracing_on"
    sleep 50
    cat "$tr/trace" > "$out/trace.txt"
    echo 0 > "$tr/tracing_on"
    echo 0 > "$tr/events/uprobes/charger_addprop/enable"
    echo '-:charger_addprop' >> "$tr/uprobe_events"
) </dev/null >/dev/null 2>&1 &
exit 0
