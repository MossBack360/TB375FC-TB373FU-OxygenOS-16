# TB375FC OxygenOS 16 关机充电界面初查（2026-11-13）

## 现象

用户观察到：关机充电时电池图形有时消失但文字仍在；短按电源键似乎切换显示；电量数字有时长时间不变，按电源键后才刷新。尚未在低电量条件下采集关机充电运行日志。

## 已提取、已确认

- 真机 `/system/bin/charger` 与 v2 ROM 解包文件 SHA-256 相同：`a4b3e3e9d37c779ffa5dced09c4faf2bf0b83cdc624b4dc06a31ef6d5f137f03`。它是 AArch64 ELF，链接 `android.hardware.health@2.0/2.1`。
- 动画配置和三张图片位于 `/product/etc/res/values/charger/animation.txt` 与 `/product/etc/res/images/charger/`；已只读提取到 `out/offmode-charger-audit-2026-11-13/`。`animation.txt` 配置 7 个循环、22 帧；`battery_scale.png` 为 22 帧，帧数匹配。百分比文字使用单独的 `percent_font.png`。
- 图片 22 帧均包含非黑色图形像素，没有全空的电池帧。动画按当前电量选择起点，高电量时每轮帧数很少，因此灭屏可能很快；不能按 22 帧 × 7 轮推定固定显示时长。
- 当前系统注册的健康服务是 AIDL；`charger` 的 HIDL 2.1 代码包含 `Charger uses system defaults` 回退路径。不能仅凭 AIDL/HIDL 版本不同断言电量读取失败。
- 正常开机时 `/sys/class/power_supply/battery/capacity` 可读；这不能证明关机充电时的定时更新正确。
- `/system/etc/init/hw/init.rc` 有 `ro.bootmode=charger` 时启动 `bspFwUpdate` 的 OPlus 分支；还需核实该服务在设备上是否实际存在、运行。
- v2 OxygenOS 的 `lk.img` 与 ColorOS 参考包的 `lk.img` 哈希不同；两者均含 `off-mode-charge` 字符串。这证明启动固件也有离线充电逻辑，但不能证明它实际绘制了用户看到的文字。

## 代码路径与判断

当前二进制包含 AOSP `healthd_mode_charger.cpp`、`HalHealthLoop.cpp` 和 `charger_utils.cpp` 的函数/日志字符串；以下行为来自对应 AOSP 源码，仍需关机充电日志确认设备实际运行路径：

1. 电源键会 `kick_animation()` 并唤亮屏幕。这解释了按键后数字才显示/刷新，不等于按键才读取电池。
2. 动画配置的循环结束后会 `blank_screen(true)`；再次按键启动动画。这能解释有意的灭屏，但正常灭屏应整屏熄灭。若文字在背光亮着时单独残留，则属于显示/图层问题。
3. `OnHealthInfoChanged()` 保存最新电量；`UpdateScreenState()` 在每个动画循环开始时把它复制到 `cur_level`，再绘制百分比。因而数字未必每次底层电量变化立即刷新；亮屏动画下一轮仍长期不变，才更像 HAL/轮询故障。
4. HealthLoop 可通过 power_supply uevent 和周期 wakealarm 更新。当前是否收到这些事件、周期是多少，关机充电日志尚未证实。
5. 对应 AOSP 绘图实现每帧先清屏，再在同一缓冲区绘制电池图片和百分比，最后 `gr_flip()`。其正常 `blank_screen()` 不会只隐藏电池图片而保留百分比。因此“只剩文字”的画面有两类候选：当前 ROM 绘图/显示栈异常，或 LK/其他启动阶段画面与 Android charger 画面交接异常；现阶段无法把其中一类定为根因。
6. 参考 AOSP 默认健康轮询在插电时为约 60 秒，另外还响应 `power_supply` uevent。即使底层已更新，动画停止后没有画面重绘；按电源键重新播放时才看到新数字，与用户的主要现象吻合。当前二进制的实际配置和离线事件仍未动态确认。

参考源码：

- https://android.googlesource.com/platform/system/core/+/refs/heads/main/healthd/healthd_mode_charger.cpp
- https://android.googlesource.com/platform/system/core/+/refs/heads/main/healthd/healthd_mode_charger_hidl.cpp
- https://android.googlesource.com/platform/system/core/+/refs/heads/main/healthd/charger_utils.cpp
- https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/health/utils/libhealthloop/HealthLoop.cpp
- https://android.googlesource.com/platform/system/core/+/79677f8b4928e1cda39b8f561001769b955fa2a0/healthd/healthd_draw.cpp

## 下一步验证

在电量低于约 80% 时，关机插电，记录“屏幕亮且数字不变”与“灭屏后再按电源数字变化”两种情况。回到 Android 后采集上一次关机充电的 kmsg/pstore，重点搜索 `charger:`, `healthd`, `battery`, `wakealarm`, `power_supply`, `blank_screen`。如果数字仅在动画结束并灭屏后不更新，属于有限显示周期；若亮屏跨多个动画循环仍不更新，再查 HealthLoop 定时更新及回退 Health 实现。若只有电池图消失而文字亮着，优先查绘图和 DRM blank，不改电池 HAL。

本轮未修改设备或制作补丁。
