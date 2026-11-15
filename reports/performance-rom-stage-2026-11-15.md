# 性能模式 ROM 固化准备（2026-11-15）

## 当前验证

- 当前平板的 `fixo_settings_companion v0.1` 已提供高性能开关到 `cmd power set-fixed-performance-mode-enabled` 的桥接。
- 在真机上将 `settings system high_performance_mode_on` 临时设为 `1` 和 `0`，桥接日志先后记录 `fixed-performance=true` 和 `false`；随后删除测试键，恢复测试前的 `null` 状态。
- 11 月 15 日在电池界面实点三档：高性能弹确认框后，设置键变 `1`，桥接日志记录 `true`，联想 `mtkpower@impl` 明确记录 `Mode::FIXED_PERFORMANCE: 1`；点均衡后设置键变 `0`，桥接记录 `false`，HAL 记录 `Mode::FIXED_PERFORMANCE: 0`。省电档使 `settings global low_power` 从 `0` 变 `1`，Android `BatterySaverController` 接收到开关；切回均衡时两者恢复 `0`。测试结束还原初始的高性能键 `null`、省电键 `0`。
- 省电档触发的 MTK Power HAL `setMode type:1` 同时报告 `unknown type`；因此只能确认 Android 省电框架已联动，不能据此声称联想 HAL 对该模式实施了额外的硬件调度。高性能档的 `FIXED_PERFORMANCE` 则有 HAL 明确确认。
- 读取开关仍是每秒一次的轻量轮询。Settings 数据库不是 init 的属性触发器，不能把它直接改成 `on property:`；尚未找到经过真机验证的事件订阅替代品。

## v5 工作树

- `system_a/system/etc/fixo/performance.sh`：从已验证的 Magisk 模块脚本提取，只把 `su -Z ... 2000` 改为直接在 init 指定的 shell UID/SELinux 域执行命令。
- `system_a/system/etc/init/fixo-performance.rc`：在 `sys.boot_completed=1` 启动服务；进程以 UID shell、`u:r:shell:s0` 运行，由 init 监督。
- `system_a/config/system_a_fs_config` 与 file contexts：已写入对应模式和标签。
- 可复现脚本：`patch/stage_performance_rom.py`，输入 `out/settings-companion-v0.1-2026-11-12/fixo-settings-companion-v0.1.zip` 与 v5 工作树。

脚本已通过 `sh -n`。尚未编译/刷入 v5，因此 **init 服务启动与开机时序未实测**。v5 实测通过后，必须停用旧 `fixo_settings_companion` 的 `service.sh` 桥接，避免两个进程重复设置 PowerManager；其 `system.prop` 两项已独立固化，不应直接删除配置。

## 磁吸补丁位置

- 源码：`patch/hall_cover_event/hall-cover.sh`
- 构建：`patch/build_hall_event_trial.py`
- ROM 固化：`patch/stage_hall_cover_rom.py`
- 真机验证过的试验包：`out/hall-event-rom-trial-2026-11-15/xiaoxin-hall-cover-rom-event-v2.1-test.zip`
- v5 工作树：`system_a/system/etc/fixo/hall-cover.sh`、`system_a/system/etc/init/fixo-hall-cover.rc`
