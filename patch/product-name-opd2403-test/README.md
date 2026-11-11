# OPD2403 product-name trial

This Magisk module changes only `ro.product.name`, which supplies `Build.PRODUCT`.
The original OxygenOS 16 SystemUI hardcodes `OPD2203` in
`NOT_SUPPORT_FULLSCREEN_WINDOW_DECOR_PRODUCTS`, but not `OPD2403`.

`OPD2403` is the official OnePlus Pad 2 model code. This is a reversible test,
not a full device identity conversion. Model, fingerprint, vendor product, and
market name remain unchanged. Disable the module and reboot to restore OPD2203.

Changing a global product property can affect other OEM and app checks; keep
this separate from the market-name module until the tablet is checked.
