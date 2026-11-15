# OxygenOS v5 charger 固化候选（2026-11-15）

工作目录：`E:\工程\github\xiaoxin Oxygen\temp3\OxygenOS_16.0.5_TB373FU_TB375FC_v2\v5-build`。原始下载包及 v3/v4 工作树保持不动；本目录是 v4-cts 工作树的独立副本。原始线刷镜像来自用户指定的 `C:\Users\GY\Documents\MEGA下载\OxygenOS_16.0.5_TB373FU_TB375FC_v2\image`。`init_boot.img` 改用用户指定的原版 `C:\Users\GY\Documents\MEGA下载\initboot oxy\init_boot.img`，SHA-256 `7138f0e13e396c57e6860b24c1f9ddb9fec77a7400347f6231ac36aab533602b`，与下载包内文件不同。

## 已暂存的 charger 文件

| 路径 | 用途 |
|---|---|
| `/system/bin/charger` | 已实测模块所用的 verbose charger；只把原二进制的日志级别提高，以提供 `animation starting/done` 事件。目标 SHA-256 `ca444a23efa4e760d23506df4e09c5249df05a9c265e9928f6844338cfae12b5`。|
| `/system/bin/charger_drm_blank` | 复用经模块测试的 DRM ACTIVE 辅助程序。SHA-256 `8c36c4469332508b3c5e99381d6380b8ed4c33f5e7db70703f7e697c47070bc8`。|
| `/system/etc/fixo/charger-watch.sh` | 监听 Power 键及 charger 动画事件；无 Magisk 路径、无 60 秒自动亮屏。|
| `/system/etc/init/fixo-charger.rc` | 在 Android init 的 `charger` 事件中启动独立服务，正常开机不运行。|

旧 `/system/bin/charger` 备份在 `v5-build/originals-before-v5/charger.original`。`patch/charger_drm_force/stage_rom.py` 校验输入 SHA-256 后才写入文件和 EROFS fs_config/file_contexts。

## 镜像处理

`v5-build/build_images.sh` 从拷贝的工作树重建 `system_a`、`system_ext_a`、`product_a`；`v5-build/assemble_super.sh` 将它们与原始 vendor/dlkm 镜像组装成原大小的 super。`product_a` 的新 EROFS 镜像可超过旧逻辑分区配额；只要组内总量与物理 super 容量允许，lpmake 重新分配逻辑分区，不修改 scatter 的物理 super 大小。

原始 `system_a_file_contexts` 中 3 条中文图标文件名被官方 Linux `mkfs.erofs` 拒绝。构建专用 ASCII 文件仅将这 3 条同为 `system_file` 的规则合并成同目录 PNG 正则，保留原始 file_contexts。v4-cts 新增 `fixo_circle_to_search.xml` 缺少 fs_config 条目，本轮补齐。

## 未验证事项

Magisk 模块曾完成一次关屏、Power 唤醒、再次关屏实测，但固化版的启动身份和 SELinux 权限可能不同。尤其 `charger` 域是否允许 `/system/bin/sh`、`dmesg` 和 `pidfd_getfd`，不能仅靠静态镜像校验确认。完成打包后仍须整机刷入测试，不能把它列为稳定版。原版 `init_boot.img` 不含 Magisk，因此剩余依赖 Magisk 的动态模块不会自动生效；见 `rom-solidification-preflight-2026-11-13.md`。
