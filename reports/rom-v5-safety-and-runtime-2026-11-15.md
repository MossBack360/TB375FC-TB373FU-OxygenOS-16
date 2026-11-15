# v5 ROM 固化：刷机范围与运行时状态（2026-11-15）

## 刷机范围

用户提供的 `initboot oxy/init_boot.img` 只作为原始参考，SHA-256 为 `7138f0e13e396c57e6860b24c1f9ddb9fec77a7400347f6231ac36aab533602b`。它已从 v5 `package/image` 移到 `v5-build/originals-before-v5/init_boot-reference.img`，不会被当前候选包刷入。

`v5-build/package/image/MT6897_Android_scatter.txt` 和 `.xml` 只把 `super` 标为 `is_download=true`；`preloader_a`、`preloader_b`、`init_boot_a`、`init_boot_b` 都为 false。`tool/option.ini` 的 `Format_All_Download` 与 `Firmware_Upgrade` 均为 false，仅 `Download_Only` 为 true。删除了复制来的 `tool/history.ini`，避免 GUI 打开旧包的 scatter。`patch/audit_safe_flash_package.py` 对 TXT/XML、`download_agent/flash.xml`、默认模式和实际 payload 执行一致性校验。

目前 v5 尚未生成 `super.img`，此包**不可刷**。即使以后生成，只能在审计通过并选用 Download Only 时使用。对 super 的重新打包会重排其内部 EROFS 数据；但本轮没有把文件写入 `my_preload` 目录，且不会单独刷写 preloader 分区。super 的物理容量与 scatter 分区地址保持原值；product 增长只在 super 内部逻辑分区重分配。

## 已写入的静态内容

`patch/stage_v5_static.py` 已把 05/06/07/23/24/27/28、Gallery-only v1.1、AI 特性 XML 和经过早期包扫描的 Settings v5.3 共 26 个文件写入 v5 的**解包工作树**，清单是 `v5-build/staged-static-files.txt`。还没有生成最终镜像。静态文件不是所有 Magisk 模块的等价替代。

`patch/stage_v5_props.py` 对稳定模块 `system.prop` 做了去重核对：相机 `debug.camera.morpho.sr.on=0`、过渡圆角 `ro.oplus.display.rc.size=26,26,26,26`、两条机型属性已在先前 v4 底树；`ro.audio.monitorRotation=true` 已在未改动的原 vendor `build.prop`。这轮新加入 `/system/build.prop` 的四条是：

```
persist.sys.oplus.nandswap.storage.min=19
ro.build.release_type=true
persist.vendor.radio.virtualcomm=1
persist.vendor.radio.virtualcomm.enable=1
```

20/30 号模块重复提供的两条属性只写一次。08 相机启动配置和 15 智能刷新 XML 已在 v4 底树，和稳定 ZIP 逐字节哈希一致；10 号底角特性表里的 feature 名称是当前 05 号统一特性表的子集，没有另行覆盖。`ro.audio.monitorRotation` 属于静态 vendor 属性；扬声器转向时调用音频服务仍是动态功能，不能混为一谈。

## Magisk 动态功能不能直接丢掉

此前准备的 `out/rom-glue-stage-2026-11-13/system/etc/init/fixo-glue.rc` 全部服务仍为 disabled，只是待审代码。直接复制它会丢失功能。必须按以下方式完成并验证：

1. `post-fs-data` 前后的自动亮度曲线选择，以及 ZUI ZRAM backing 大小生成，必须赶在 framework 读取配置和 vendor `swapon_all` 之前。
2. AI provider、显示 PQ、底角模式、磁吸盖、扬声器旋转、注视屏幕、抬起亮屏、性能模式和通信共享需要 init 监管的运行时服务或等效原生逻辑；不能只放 APK/XML。
3. 每项服务要验证实际 UID、SELinux domain、系统属性权限、Settings/PackageManager/PowerManager 可用时机和失败退出行为。原 Magisk `su -Z` 或 `resetprop` 不会在无 Magisk 的 ROM 中自动可用。
4. 关机 charger 辅助服务也尚未验证在 ROM 原生 `charger` domain 下有足够的 DRM/进程权限；此前成功样本来自 Magisk 模块，不等于原生 init 服务成功。

因此在这些功能完成或明确标注保留外部依赖前，**不生成可刷的完成版，不刷设备**。如果以后确实必须修改 `init_boot`，以本次参考镜像为输入生成新的有版本号镜像，并将其单独加入刷机白名单；绝不把参考原版当最终补丁。

## 已核对的 ZUI 时序线索

原 vendor 的 `/vendor/etc/init/init.extend_reclaim.rc` 在 `sys.boot_completed=1` 触发 `swapon_zram`，随后 `swapon_all /vendor/etc/fstab.zram_wb`；`init.mt6897.rc` 和 `init.project.rc` 还引用 `/vendor/etc/fstab.enableswap`。原 fstab 使用 `zram_backingdev_size=prop`，历史 Magisk 补丁则在 post-fs-data 按 OPlus 设置值生成实际大小（0/2/4/6/8GB 等）。固化时需要先确认 `prop` 在本机 fs_mgr 中如何解析；不能把运行期 writeback 脚本视为前期 backing 配置的替代。
