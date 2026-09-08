#!/system/bin/sh

while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done

pm grant com.dolby.daxservice android.permission.INTERACT_ACROSS_USERS_FULL >/dev/null 2>&1
dax_pid="$(pidof com.dolby.daxservice)"
[ -n "$dax_pid" ] && kill -9 $dax_pid
am startservice -n com.dolby.daxservice/.DaxService >/dev/null 2>&1
