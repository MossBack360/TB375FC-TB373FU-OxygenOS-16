#!/system/bin/sh
pids="$(pidof fixo_wake_glue 2>/dev/null)"
[ -n "$pids" ] && kill $pids 2>/dev/null
