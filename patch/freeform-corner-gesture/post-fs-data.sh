#!/system/bin/sh

MODDIR=${0%/*}
src="$MODDIR/payload/com.oplus.oplus-feature.xml"
dst=/my_product/etc/extension/com.oplus.oplus-feature.xml

[ -f "$src" ] || exit 1
[ -f "$dst" ] || exit 1
chmod 0644 "$src"
chcon u:object_r:system_file:s0 "$src" >/dev/null 2>&1
mount --bind "$src" "$dst"
