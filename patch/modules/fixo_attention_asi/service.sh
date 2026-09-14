#!/system/bin/sh
MODDIR=${0%/*}
HELPER="$MODDIR/attention-useractivity.apk"
LOG="$MODDIR/runtime.log"

write_log() {
  if [ -f "$LOG" ] && [ "$(wc -c <"$LOG" 2>/dev/null)" -gt 262144 ]; then
    mv -f "$LOG" "$LOG.old"
  fi
  printf '%s %s\n' "$(date '+%F %T')" "$*" >>"$LOG"
}

until [ "$(getprop sys.boot_completed)" = 1 ]; do sleep 2; done

pm grant com.google.android.as android.permission.CAMERA >/dev/null 2>&1

while true; do
  result="$(cmd attention setTestableAttentionService com.google.android.as 2>&1)"
  component="$(cmd attention getAttentionServiceComponent 2>&1)"
  write_log "bind result=$result component=$component"
  [ "$result" = true ] && break
  sleep 5
done

if [ "$(settings get secure adaptive_sleep 2>/dev/null)" = null ]; then
  settings put secure adaptive_sleep 1
  write_log "adaptive_sleep initialized to 1"
fi

last_check=0
while true; do
  [ "$(settings get secure adaptive_sleep 2>/dev/null)" = 1 ] || {
    sleep 3
    continue
  }

  power="$(dumpsys power 2>/dev/null)"
  printf '%s\n' "$power" | grep -q 'mWakefulness=Awake' || {
    sleep 2
    continue
  }

  last="$(printf '%s\n' "$power" | sed -n 's/.*lastUserActivityTime=\([0-9][0-9]*\).*/\1/p' | head -n 1)"
  timeout="$(printf '%s\n' "$power" | sed -n 's/^Screen off timeout: \([0-9][0-9]*\) ms.*/\1/p' | head -n 1)"
  now_sec="$(cut -d. -f1 /proc/uptime 2>/dev/null)"

  case "$last:$timeout:$now_sec" in
    *[!0-9:]*|::*|*::*) sleep 2; continue ;;
  esac

  now_ms=$((now_sec * 1000))
  remaining=$((last + timeout - now_ms))
  since_check=$((now_ms - last_check))

  if [ "$remaining" -le 6000 ] && [ "$remaining" -gt 0 ] && [ "$since_check" -ge 4000 ]; then
    last_check=$now_ms
    start="$(date +%s).000"
    dispatched="$(cmd attention call checkAttention 2>&1)"
    sleep 2
    line="$(logcat -d -v epoch -T "$start" -s AiAiAttention:I '*:S' 2>/dev/null | grep 'completed in' | tail -n 1)"
    face="$(printf '%s\n' "$line" | sed -n 's/.*; \([0-9][0-9]*\) frames had face detected, .*/\1/p')"
    gaze="$(printf '%s\n' "$line" | sed -n 's/.*, \([0-9][0-9]*\) frames had gaze detected, .*/\1/p')"
    [ -n "$face" ] || face=0
    [ -n "$gaze" ] || gaze=0

    if [ "$face" -gt 0 ] && [ "$gaze" -gt 0 ]; then
      CLASSPATH="$HELPER" app_process /system/bin com.fixo.attention.UserActivity >/dev/null 2>&1
      write_log "present face=$face gaze=$gaze remaining=${remaining}ms dispatch=$dispatched"
    else
      write_log "absent face=$face gaze=$gaze remaining=${remaining}ms dispatch=$dispatched"
    fi
  fi

  sleep 1
done
