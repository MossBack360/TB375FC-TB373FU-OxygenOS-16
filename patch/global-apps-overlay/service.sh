#!/system/bin/sh
MODDIR=${0%/*}

apply_one() {
    target="$1"
    payload="$2"
    package="$3"

    [ -f "$target" ] && [ -f "$payload" ] || return 1
    chmod 0644 "$payload" || return 1
    chcon u:object_r:system_file:s0 "$payload" || return 1
    mount --bind "$payload" "$target" || return 1
    am force-stop "$package" || true
    for pid in $(pidof "$package"); do
        kill -9 "$pid" || true
    done
    sha256sum "$target"
}

if [ "$1" = "--apply" ]; then
    apply_one \
        /my_stock/priv-app/KeKeUserCenter/KeKeUserCenter.apk \
        "$MODDIR/payload/KeKeUserCenter.apk" \
        com.oneplus.account || exit 1
    apply_one \
        /my_stock/priv-app/OppoGallery2/OppoGallery2.apk \
        "$MODDIR/payload/OppoGallery2.apk" \
        com.oneplus.gallery || exit 1
    log -t FixOGlobalApps "Applied global account and gallery overlay"
    exit 0
fi

until [ "$(getprop sys.boot_completed)" = "1" ]; do
    sleep 1
done

su -mm -c "sh '$MODDIR/service.sh' --apply" >"$MODDIR/runtime.log" 2>&1
