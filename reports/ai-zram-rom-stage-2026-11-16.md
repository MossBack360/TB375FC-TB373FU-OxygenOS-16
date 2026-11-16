# 05 AI and 18 ZUI memory expansion: v5 ROM staging

The owner confirmed the 09 PQ test. This change stages 05 and 18 in the unpacked v5 tree; it does not rebuild or flash an image.

## 05 AI providers

- Source: `temp3/稳定安装/01-当前启用-Magisk/05-oneplus-ai-providers-v2.9-international-defaults.zip`, SHA-256 `989a6f3e7ba461a9ab60e183a4b0783c38fc3b3b8caa318ffe86ef319b833509`.
- The AI APKs and the two non-merged feature XML files were already in v5 and were checked byte-for-byte against the ZIP. The unified feature table already contains `finger_flashnotes_enable` and the accepted bottom-corner features.
- New `system/etc/init/fixo-ai-providers.rc` starts `system/etc/fixo/ai-providers.sh` at `sys.boot_completed=1` as UID 2000 in `u:r:shell:s0`. The script preserves the source module's twelve package-enable attempts and 15-second DMP setting sync. It directly calls `settings`, removing the Magisk `su -Z` dependency. Log: `/data/local/tmp/fixo-ai-providers.log`.

## 18 ZUI ZRAM writeback

- Source: `temp3/稳定安装/01-当前启用-Magisk/18-zui-zram-writeback-memory-expansion-v0.6-test.zip`, SHA-256 `6d4bfa8ddac9ba7ed1b0b73474bff01185aea038977b7bf7050902179cca6735`.
- `system/etc/init/fixo-zram-writeback.rc` handles `load_persist_props_action` after persistent Settings properties are loaded. It bind-mounts one of seven static fstab lines from `system/etc/fixo/zram/` over both ZUI vendor fstab paths. Off uses `0`; enabled sizes 2/4/6/8/12/16 use their corresponding GiB backing size. Each line keeps `zramsize=100%`. This is before the vendor `swapon_all` actions at boot complete. An unset or invalid enabled size falls through to the stock fstab and needs first-boot inspection.
- The same RC starts `system/etc/fixo/zram-writeback.sh` after boot complete. It preserves the confirmed module's temperature gate, 30-minute idle marking, 30-minute settle period, 32 MiB per-cycle limit, and 9000-second interval. Log: `/data/local/tmp/fixo-zram-writeback.log`.
- Root UID in the shell SELinux domain could not read or write `sysfs_zram` on the current device. The v5 `system_ext_sepolicy.cil` therefore adds `(allow shell sysfs_zram (file (getattr open read write)))`. No kernel or vendor binary is replaced.

## Validation and boundary

- Staging script: `patch/stage_ai_zram_rom.py`; it checks both exact source ZIP hashes and refuses to overwrite differing staged files. It also adds fs_config and file-context entries. Re-running it was idempotent.
- The two new shell scripts passed `sh -n` on the tablet. Existing AI payload files matched the source ZIP. At the time of staging, neither 05 nor 18 was active, so the then-observed `backing_dev=none` was not a test of this v5 stage.
- Native init parsing, bind mounts, policy compilation and service operation still need a v5 ROM boot. Do not call the unpacked tree flash-ready. On first boot, check both mounted fstab contents before `swapon_all`, `backing_dev`, `/proc/swaps`, service state, DMP value, and service logs. Disable duplicate Magisk 05/18 modules if this ROM stage is used.

## Same-day current-ROM Magisk test

The owner correctly noted that the prior v5 staging had not installed either module on the current tablet. Before installation, neither module ID was present, all three AI `pm path` queries were empty, and ZRAM `backing_dev=none` despite `persist.sys.oplus.nandswap=true` and size `4`.

Installed the two unchanged archived ZIPs under module IDs `fixo_opd2514_ai_addons` and `fixo_zui_zram_writeback`, then rebooted. `sys.boot_completed=1`, SystemUI PID 2284, and neither module has a disable marker. PackageManager now reports `/system/app/AIMemory/AIMemory.apk`, `/system/app/AIPaint/AIPaint.apk`, and `/system/priv-app/DMP/dmp.apk`; all three are enabled. AI runtime log reports 12 sync attempts and `com.oplus.dmp.aiask.disable=1`. Its three mounted feature XML hashes match the v5-staged files; the unified table retains the freeform profile.

ZRAM module log reports `enabled=true size=4 backing=4G`; both mounted ZUI fstabs contain `zramsize=100%,zram_backingdev_size=4G`. Kernel `backing_dev=/dev/block/loop48`; `blockdev --getsize64` returned `4294967296` bytes, and loop48 is backed by `/data/per_boot/zram_swap`. `/proc/swaps` retains the 12 GB zram0 entry. A manual `service.sh once` run passed the live SKIN temperature gate and logged `writeback result=ok before=0 after=1 remaining=8191`; `bd_stat` changed to `1 0 1`, proving a bounded kernel writeback request completed. This tests the Magisk implementation on the current ROM, not the v5 native init adaptation.
