# 关机充电显示分支反汇编（2026-11-14）

目标仅为显示链；没有修改平板、二进制或镜像。工具：WSL `llvm-objdump-18`，OxygenOS `charger` SHA-256 `a4b3e3e9d37c779ffa5dced09c4faf2bf0b83cdc624b4dc06a31ef6d5f137f03`，ColorOS 参考 `charger` SHA-256 `09b3c8796ca09b311bab84fee97455a995643e2f8bb36fc3911a6265091a544f`。Windows REA 可识别 ARM64 ELF，但当前没有可用的原生反编译提供者，故以下为实际指令与 AOSP 源码对照，不称为完整伪代码。

## 已确认的分支

- OxygenOS `0x19fdc–0x1a098` 与 ColorOS `0x19fcc–0x1a088` 的“动画结束”路径控制流和操作对应一致，地址相差约 `0x10`，字符串地址不同。两者均检查循环数与当前轮次，重置动画，调用显示对象虚函数 `blank_screen(true, drm_)`，随后把内部 `screen_blanked_` 标为 true，并记录 `animation done`。调用没有返回值检查，也没有失败重试。不能将这里简单判为 OxygenOS 独有的条件写错。
- 当前产品 `animation.txt` 为 7 轮；结束后按上面路径本应尝试关屏。电源键重新 kick 动画会导致重绘，电量数字可在新一轮绘制时刷新。亮着的静态圆环/旧数字符合“最后一帧保留而熄屏未完成”，但还不能断定失败发生在调用前、DRM/FBDEV 后端，还是显示输出阶段。
- AOSP `HealthdDraw::blank_screen()` 将动作交给 `gr_fb_blank()`，再由 minui 的实际图形后端执行。当前二进制同时包含 DRM 和 FBDEV 相关代码与错误字符串，例如 `Atomic Commit Blank_Sec failed`、`ioctl(): blank`、`Unsupported multiple connectors`；静态存在不证明本次启动选用了哪个后端。ColorOS 对应 `Atomic Commit Blank_Sec failed` 路径的指令也与 OxygenOS 对应，不能因为二进制哈希不同就整体替换。
- AOSP `Charger::SetSwCallback(SW_LID)` 可切换内/外 DRM 显示编号，当前二进制的主显示变量在熄屏时作为参数传入。TB375FC 有磁吸盖传感器，但尚未证实 charger 模式会收到 `SW_LID` 事件或选错连接器；这只保留为待验证假设。

## 下一步只需分开两个问题

1. 关机充电的最后一次 `animation done` 是否确实发生？若未发生，查计时/事件循环；若发生，继续看后端。
2. 当次 `blank_screen(true, drm_)` 选用了哪个图形后端和连接器？抓 pstore/kmsg 中 `charger`、`Atomic Commit`、`ioctl(): blank`、`Unsupported multiple connectors`、DRM/背光错误。若状态被标为 blank 但物理屏幕仍亮，再针对实际后端做最小修复；先不改电池 HAL 或动画素材。

本次用户正常开机后 ADB 可连接，但 Magisk/`su` 不存在；`/sys/fs/pstore`、`dmesg` 对 shell 拒绝访问，`logcat -L` 报 `No such file or directory`，所以未能取得关机充电运行日志。同一启动的 ZuiCamera 和 Settings APK 均读回原 ROM SHA-256，确认此前 Magisk 挂载的候选这次没有生效。设备状态不变，待确认 Root/boot 镜像为何变化后再采样。

AOSP 对照：`healthd_mode_charger.cpp`（`UpdateScreenState`、`ProcessKey`、`SetSwCallback`）、`healthd_draw.cpp`（`blank_screen`）、`minui/graphics.cpp`（`gr_fb_blank`）、`minui/graphics_drm.cpp`（连接器 blank）。这些是同源实现的解释依据，不证明本机运行态。
