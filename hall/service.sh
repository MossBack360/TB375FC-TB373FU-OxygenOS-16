#!/system/bin/sh
# TB375FC calibration: hall_status 1=open, 0=closed.
MODDIR=${0%/*}
STATE_NODE=/sys/bus/platform/drivers/hall/hall_status
LAST_STATE=
READER=

read_state() { cat "$STATE_NODE" 2>/dev/null; }
message() { log -t XiaoxinHall "$*"; }

sync_state() {
    state=$(read_state) || return
    case "$state" in
        0) key=KEYCODE_SLEEP; label=closed ;;
        1) key=KEYCODE_WAKEUP; label=open ;;
        *) return ;;
    esac
    [ "$state" = "$LAST_STATE" ] && return
    if input keyevent "$key"; then
        LAST_STATE=$state
        message "$label -> $key"
    else
        message "Failed: $label -> $key"
    fi
}

on_event() {
    case "$1:$2:$3" in
        0001:00fc:00000001|0001:00fd:00000001) sync_state ;;
    esac
}

# Exercise the actual dispatcher with fake sensor/input functions; no screen changes.
if [ "${1:-}" = --self-test ]; then
    read_state() { printf '%s\n' "$TEST_STATE"; }
    message() { :; }
    input() { [ "$FAIL_INPUT" = 1 ] && return 1; ACTIONS="$ACTIONS $2"; }
    ACTIONS=; FAIL_INPUT=0; TEST_STATE=0
    on_event 0001 00fc 00000001
    on_event 0001 00fc 00000000
    on_event 0001 00fd 00000001
    TEST_STATE=1
    on_event 0001 00fc 00000002
    on_event 0000 0000 00000000
    on_event 0001 0074 00000001
    [ "$ACTIONS" = ' KEYCODE_SLEEP' ] || exit 1
    on_event 0001 00fc 00000001
    TEST_STATE=bad
    on_event 0001 00fd 00000001
    TEST_STATE=0; FAIL_INPUT=1
    on_event 0001 00fd 00000001
    [ "$LAST_STATE" = 1 ] || exit 1
    FAIL_INPUT=0
    on_event 0001 00fd 00000001
    [ "$ACTIONS" = ' KEYCODE_SLEEP KEYCODE_WAKEUP KEYCODE_SLEEP' ] || exit 1
    echo 'PASS: close/open, UP/repeat/duplicate/unrelated filtering, invalid state, failed-action retry'
    exit 0
fi

exec 9>"$MODDIR/daemon.lock"
flock -n 9 9>&9 || exit 0
FIFO=$MODDIR/events.fifo
cleanup() {
    [ -n "$READER" ] && kill "$READER" 2>/dev/null
    [ -n "$READER" ] && wait "$READER" 2>/dev/null
    rm -f "$FIFO" "$MODDIR/daemon.pid"
}
trap cleanup EXIT
trap 'exit 0' INT TERM
echo $$ > "$MODDIR/daemon.pid"
while [ "$(getprop sys.boot_completed)" != 1 ]; do sleep 2; done
rm -f "$FIFO"
mkfifo -m 600 "$FIFO" || exit 1

while :; do
    DEVICE=
    for node in /sys/class/input/event*/device/name; do
        [ "$(cat "$node" 2>/dev/null)" = hall ] || continue
        event=${node%/device/name}
        DEVICE=/dev/input/${event##*/}
        break
    done
    if [ ! -r "$STATE_NODE" ] || [ ! -r "$DEVICE" ]; then
        sleep 5
        continue
    fi
    getevent -q "$DEVICE" > "$FIFO" 2>/dev/null &
    READER=$!
    exec 4<"$FIFO"
    message "Listening on $DEVICE; 0=closed, 1=open"
    LAST_STATE=
    sync_state
    while read -r type code value <&4; do
        on_event "$type" "$code" "$value"
    done
    exec 4<&-
    wait "$READER" 2>/dev/null
    READER=
    message 'Input reader stopped; reconnecting in 5 seconds'
    sleep 5
done
