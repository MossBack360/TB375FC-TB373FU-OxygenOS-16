#!/system/bin/sh
MODDIR=${0%/*}
DEX="$MODDIR/wake-glue.dex"
LOG="$MODDIR/runtime.log"

until [ "$(getprop sys.boot_completed)" = 1 ]; do sleep 2; done

daemon_alive() {
  [ -n "$(pidof fixo_wake_glue 2>/dev/null)" ]
}

stop_daemon() {
  pids="$(pidof fixo_wake_glue 2>/dev/null)"
  [ -n "$pids" ] && kill $pids 2>/dev/null
}

start_daemon() {
  printf '%s starting daemon\n' "$(date '+%F %T')" >>"$LOG"
  CLASSPATH="$DEX" app_process /system/bin --nice-name=fixo_wake_glue \
    com.fixo.wake.WakeGestureDaemon >>"$LOG" 2>&1 &
}

stop_daemon
while true; do
  enabled="$(settings get global ambient_tilt_to_wake 2>/dev/null)"
  if [ "$enabled" = 1 ]; then
    daemon_alive || start_daemon
  else
    stop_daemon
  fi
  sleep 3
done
