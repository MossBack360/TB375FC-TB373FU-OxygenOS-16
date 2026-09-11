#!/system/bin/sh

# OxygenOS FlexibleWindowUI already contains the tutorial and gesture code.
# This module only enables the panorama/freeform feature gate used by it.
resetprop persist.oplus.panorama.branch.enable true

# Keep the feature from being disabled by the secure state gate.
settings put secure panoramic_forced_disable_state 0 >/dev/null 2>&1
am force-stop com.oplus.pscanvas >/dev/null 2>&1

log -t FixOFreeform "corner-to-freeform gate enabled"
