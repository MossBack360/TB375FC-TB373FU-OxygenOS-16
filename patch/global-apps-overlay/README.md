# FixO global account and gallery

Post-boot Magisk overlay for two APKs that should survive reflashes of the
OxygenOS port:

- `/my_stock/priv-app/KeKeUserCenter/KeKeUserCenter.apk`
- `/my_stock/priv-app/OppoGallery2/OppoGallery2.apk`

The account payload is the verified OPD global `KeKeUserCenter` donor. The
gallery payload is the newer backed-up OnePlus export build, not the older
OPD2203 reference package.

The module bind-mounts after `sys.boot_completed=1` so Android package scanning
can finish against the base ROM, then force-stops the affected apps so the next
launch uses the mounted payload.
