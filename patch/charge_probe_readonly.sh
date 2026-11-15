#!/system/bin/sh
# Read-only charge sampling. Starts in normal Android and stops after 30 min.
out=/sdcard/Download/tb375fc-charge-probe.csv
value() {
    cat "/sys/class/power_supply/$1/$2" 2>/dev/null | tr -d '\r\n'
}
if [ ! -s "$out" ]; then
    echo 'time,capacity,status,gauge_charge_counter_uAh,gauge_current_uA,battery_voltage_uV,primary_online,primary_input_limit,primary_status' > "$out"
else
    echo "# sampling resumed $(date +%FT%T%z)" >> "$out"
fi
i=0
while [ "$i" -lt 180 ]; do
    echo "$(date +%FT%T%z),$(value battery_mm8013 capacity),$(value battery_mm8013 status),$(value battery_mm8013 charge_counter),$(value battery_mm8013 current_now),$(value battery_mm8013 voltage_now),$(value primary_chg online),$(value primary_chg input_current_limit),$(value primary_chg status)" >> "$out"
    i=$((i + 1))
    sleep 10
done
