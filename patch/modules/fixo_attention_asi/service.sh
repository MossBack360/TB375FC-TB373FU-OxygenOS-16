#!/system/bin/sh
MODDIR=${0%/*}
LOG="$MODDIR/runtime.log"

until [ "$(getprop sys.boot_completed)" = 1 ]; do sleep 2; done

grant=$(pm grant com.google.android.as android.permission.CAMERA 2>&1)
result=$(cmd attention setTestableAttentionService com.google.android.as 2>&1)
component=$(cmd attention getAttentionServiceComponent 2>&1)
printf 'grant=%s\nset_result=%s\ncomponent=%s\n' "$grant" "$result" "$component" >"$LOG"
