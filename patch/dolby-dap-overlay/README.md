# FixO Dolby DAP bridge v1.2

适用于 TB375FC/TB373FU 的 OxygenOS 16 移植版。

模块在现有 MT6897 vendor Dolby 库上注册 DAP，恢复 ZUI `DaxService`，并补齐它访问 DMS HAL 所需的权限和 SELinux 规则。安装后重启生效。

已在 OPD2203 移植系统上验证：DAP 被 AudioFlinger 注册并启用，`DaxService` 能接收 `DAP_PARAMS_UPDATE`，设置页可在“智能”和“影院”间切换且无 Dolby AVC。
