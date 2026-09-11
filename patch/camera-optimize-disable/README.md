# FixO Disable Oplus Camera Startup Optimization

Replaces `/system_ext/etc/sys_camera_optimize_config.xml` with a valid disabled configuration.

The stock policy targets WeChat `BaseScanUI` and the Alipay scanner and enables memory release, delayed components, process freezing, and GC suppression. On the TB375FC OxygenOS port, the WeChat scanner can stall during Activity startup and trigger an input ANR.

This module leaves camera HAL settings and the global fullscreen caption feature unchanged. Uninstalling the module restores the stock file.

Version 1.1 uses an early bind mount because this ROM's Magisk setup does not automatically mount a module-level `system_ext` tree.

Confirmed working on TB375FC: WeChat Scan no longer stalls or returns through the globe loading screen after reboot.
