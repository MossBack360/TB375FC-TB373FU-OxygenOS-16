#!/system/bin/sh
# Temporary tmpfs pressure for the next scheduled ZRAM writeback test.
set -eu

mb=${1:-3072}
hold=${2:-3600}
case "$mb:$hold" in *[!0-9:]*|:*|*:) echo 'usage: sh zram-cold-page-probe.sh [MiB 256..4096] [hold seconds 60..7200]' >&2; exit 2;; esac
[ "$mb" -ge 256 ] && [ "$mb" -le 4096 ] &&
    [ "$hold" -ge 60 ] && [ "$hold" -le 7200 ] || exit 2

available=$(awk '/^MemAvailable:/ {print int($2 / 1024)}' /proc/meminfo)
[ "$available" -gt $((mb + 2048)) ] || {
    echo "insufficient free memory: ${available} MiB available" >&2
    exit 1
}

file=/tmp/fixo-zram-probe.$$
trap 'rm -f "$file"' EXIT HUP INT TERM
before=$(awk '$1 ~ /zram0$/ {print $4}' /proc/swaps)
echo "creating ${mb} MiB temporary tmpfs data; ZRAM used before=${before:-unknown} KiB"
dd if=/dev/urandom of="$file" bs=1048576 count="$mb"
after=$(awk '$1 ~ /zram0$/ {print $4}' /proc/swaps)
echo "ZRAM used after=${after:-unknown} KiB; holding idle for ${hold}s; Ctrl-C cleans up"
sleep "$hold"
