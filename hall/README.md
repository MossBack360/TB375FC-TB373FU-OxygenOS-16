# Xiaoxin Pad Pro 2025 Hall Cover Module

这是已经在 TB375FC / 小新 Pad Pro 2025 上确认工作的保护盖脚本版本。

- `hall_status=1` 表示保护盖打开。
- `hall_status=0` 表示保护盖合上。
- 监听内核的 `hall` input 设备事件，只把 `00fc/00fd` 的 `DOWN` 当作触发信号。
- 触发后重新读取 `/sys/bus/platform/drivers/hall/hall_status`，合盖发送 `KEYCODE_SLEEP`，开盖发送 `KEYCODE_WAKEUP`。
- 脚本带单实例锁，避免同一个模块目录重复启动。
- 不修改 Settings，不改 framework，不改 SELinux。

当前设备上跑通的是 `/data/local/tmp/fixo-hall-test/service.sh` 的临时测试实例；它没有安装成 Magisk 模块，重启后会停止。

要永久启用，刷入归档里的 `xiaoxin-hall-confirmed-magisk.zip`，然后重启。Magisk 会在 `late_start service` 阶段自动执行 `service.sh`。如果之后禁用/卸载模块或移除 Magisk，这个功能也会停止。

已确认：

- 本机打开保护盖读数为 `1`。
- 本机合上保护盖读数为 `0`。
- 用户实机确认合盖息屏、开盖亮屏可用。
- `sh --self-test` 和 Magisk BusyBox `ash --self-test` 均通过。

注意：

- 这个模块和 Settings 修复模块是两个不同模块，可以共存。
- 当前临时测试脚本和刷入后的模块不要长期同时跑；正常重启后临时脚本会消失，只剩 Magisk 模块启动。
- 启动后脚本阻塞等待 input 事件，不做连续轮询，也不持有 wakelock。

