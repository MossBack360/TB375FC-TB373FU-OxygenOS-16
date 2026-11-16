# 09 画质 PQ：v1.1 模块与 v5 ROM 固化

## 真机证据

- 原 09 v1.0 每 2 秒读两个设置值，仅在变化或 `vendor.mediatek.hardware.pq_aidl-service` 重启时调用 `pqctl.jar`。保留该频率。
- v1.1 只修脚本返回值判断：`PqCtl` 即使 HAL 返回 `false` 也会以进程退出码 0 结束；旧脚本因此可能误记成功。新脚本只在输出为 `true` 时更新上次应用值，失败会重试。
- 真机安装 v1.1 后，开机服务进程存在，模块脚本和 JAR 的 SHA-256 与本地一致。临时写入 `oplus_customize_color_mode=1/0`，日志分别为 `natural preset=2 result=true`、`vivid preset=1 result=true`；临时写入 `setting_enable_color_temperature_regulation=1/0`，日志均为 `result=true`。测试后两个 Settings 键均恢复到原来的 `null`。
- 同一 JAR 以 shell SELinux 域执行时最初返回 `false`。审计日志确认缺 `mtk_hal_pq_hwservice:hwservice_manager find` 和 `mtk_hal_pq:binder call`。临时加载这两条规则后，以 root UID、`u:r:shell:s0` 执行自适应色温及鲜艳预设均返回 `true`。该临时策略将在重启后撤销。

## v5 工作树

- `system_a/system/etc/fixo/display-pq.sh` 和 `pqctl.jar`：v1.1 模块的相同逻辑，JAR 路径换为 ROM 路径。
- `system_a/system/etc/init/fixo-display-pq.rc`：`sys.boot_completed=1` 启动，root UID、shell SELinux 域。
- `system_ext_a/etc/selinux/system_ext_sepolicy.cil`：仅追加上述两条 PQ 权限；原始 CIL SHA-256 为 `ae9ce3a2a9ce4efddcd6c7c4807dd1c8d7c3dc557d39e42b815591029236afe4`。
- 已用平板 `/system/bin/secilc` 结合当前完整分区 CIL 进行离线编译，退出码 0；候选 CIL 与 v5 工作树写入后的文件逐字节相同。Shell 脚本通过 `sh -n`。
- 可复现构建：`patch/build_display_pq_v1_1.py`；可复现固化：`patch/stage_display_pq_rom.py`。

**尚未编译或刷入 v5 镜像。** ROM 中 `init` 启动时机、策略加载与 PQ 服务重启后的行为仍需首次刷机验证；届时应停用 `fixo_display_pq` Magisk 模块，防止两个桥接同时运行。旧 v1.0 ZIP 保留作回退。

用户随后确认 09 v1.1 实机测试效果正常。此确认针对当前 Magisk 模块；v5 原生 init 服务仍待首次刷机验证。
