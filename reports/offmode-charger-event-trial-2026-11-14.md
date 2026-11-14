# 关机充电显示事件补丁试验（2026-11-14）

目标：修复动画结束后静态电池画面与旧电量数字停留。仅修改关机充电模式，未触及电池 HAL。

## 本次实际装入

- `fixo_charger_verbose_trial` 临时模块：对原 `/system/bin/charger`（SHA-256 `a4b3e3e9d37c779ffa5dced09c4faf2bf0b83cdc624b4dc06a31ef6d5f137f03`）仅把 `klog_set_level(6)` 改为 `klog_set_level(7)`，开启原有 `LOGV`，无功能逻辑改动。
- `/data/adb/post-fs-data.d/charger_backlight_event_trial.sh`：只在 `ro.bootmode=charger` 下监听 `charger: animation done`，将 `/sys/class/leds/lcd-backlight/brightness` 写为 0；在 `animation starting` 时恢复原亮度。
- `/data/adb/post-fs-data.d/charger_offmode_trace.sh`：只读采样服务、背光、DPMS 和内核日志。

上述三项仍是**试验件**，不是稳定修复。原始记录在 `out/charger-offmode-event-trial-2026-11-14/`，不入 Git。

## 实测结果

- 关机充电模式约 13 秒启动第一轮动画，约 30.024 秒结束。事件脚本在 30.027 秒写入背光 0；MTK 驱动记录 `Set lcd-backlight directly ... L:0 map:0`。采样中背光一直为 0，直到约 131.56 秒电源键启动下一轮。
- 第一次结束前 `charger` 绘制了 `frame #0` 和 `82%` 文字；后续电源键触发的动画在第 17 帧之后结束，没有相同的末帧重绘。
- 后续各轮结束同样写入背光 0。用户观察：后续亮屏再暗正常，但**第一次动画结束后只剩文字，持续亮着**；已排除只是动画开始前的短暂初始画面。
- `/sys/class/drm/card0-DSI-1/dpms` 在整个 charger 过程仍为 `On`；本次内核日志仅在动画启动时出现 `UNBLANK` 通知，结束时没有对应 `BLANK` 通知。不能仅据此断言 DRM API 失败，因为该节点是否跟随 charger 使用的 DRM blank 路径尚未验证。
- `sys.boot_completed=1`，正常开机后 root 可用。临时模块和两个 post-fs-data 脚本仍在，待这次诊断结束清理或转正。

## 下一步判别

已建立 `patch/charger_backlight_event_delay_trial.sh`：保留立即写 0，再在 1 秒后、且亮度没有被新动画恢复的前提下补写 0，并记录硬件亮度节点。它已替换平板上的旧事件脚本。随后一轮开关机日志只采到 16 秒左右的动画，未到约 30 秒的 `animation done`，所以**尚不能判断这版是否有效**。下次让首次动画完整结束并停留约 5 秒，再读 `done`/`late-off` 记录。`mt_brightness_hw_changed` 在正常 Android 上是只读节点，本轮 charger 模式中尚未得到值。

用户再次报告首次充电画面不熄；第二次日志同样在约 17 秒时停止，仍没有 `animation done` 或 `late-off`。此时前述脚本尚未触发，不能把这次肉眼结果用于判断延迟补写是否有效。待确认用户是否在 17 秒左右按键开机，以及所谓“第一轮”是动画单圈还是完整充电动画序列。

随后获得有效的完整试验：第一轮 `animation done` 在 29.802 秒；立即写入 `brightness=0`，一秒后的 `late-off` 再次写入 0。此后取样至 188 秒均保持 `brightness=0`、`dpms=On`、`charger=running`、HWC 和 SurfaceFlinger 停止。用户仍观察到文字持续亮着。因此延迟补写试验**失败**；其脚本已从平板移除，恢复先前后续轮次有效的事件脚本。内核日志没有出现关屏时的 BLANK notifier；目前最值得追的是 `charger` 使用的 DRM/minui 关屏调用及返回值。AOSP `MinuiBackendDrm::DrmDisableCrtc()` 调用 `drmModeSetCrtc(..., fb_id=0, connector_count=0)` 但不检查返回码，故 `animation done` 不能证明 CRTC 确实被关闭。正常 Android 熄屏时同一 `card0-DSI-1/dpms` 为 `Off`。

首次只读 kretprobe `drm_mode_setcrtc` 在 50 秒窗口内没有任何命中，虽然 `charger` 约 29.98 秒完成动画；探针注册本身已在正常系统验证成功。故当前 `charger` 不能直接按上述 AOSP 旧式 CRTC 路径处理。现有二进制包含 `Atomic Commit Blank_Sec failed`、`Atomic commit failed`、`ro.charger.disable_init_blank` 字符串，反汇编可见原子提交分支。REA 在 Windows 上没有可用的 ARM64 ELF 深度分析 provider，因此用 WSL `llvm-objdump-18` 核对。已把单一探针替换为 `charger_drm_atomic_probe_trial.sh`，下轮只读采集 `drm_mode_atomic_ioctl` 与 `drm_mode_setcrtc` 的返回值。

第二次只读探针确认：`charger` 从启动到第一轮结束的 18 次 `drm_mode_atomic_ioctl` 调用均返回 `0`，最后一次在 30.627037 秒、`animation done` 前约 11 微秒；`drm_mode_setcrtc` 仍零命中。说明当前确实走原子提交，接口未报错；但单看返回值不能知道最后提交是否把主显示的 `ACTIVE` 属性置 0。

用 WSL 反汇编定位 `/system/bin/charger` 中静态链接的 DRM `AtomicAddProperty` 包装函数入口 `0x27910`；AArch64 入参分别为请求、对象 ID、属性 ID、值。已验证 tracefs uprobe 可在此地址注册，并把探针替换为 `charger_drm_property_probe_trial.sh`（只在 charger 模式采 50 秒，之后自动撤除）。等待下次正常开机读取属性轨迹。

第三次属性 uprobe 注册成功但没有命中；这不证明 charger 没有设置属性，可能是二进制 bind mount 的 inode 与 probe 注册对象不一致。此探针与长时只读采样脚本现已从 `/data/adb/post-fs-data.d/` 移除。设备保留 `fixo_charger_verbose_trial`（只调高 charger 日志等级）和 `charger_backlight_event_trial.sh`（后续轮次部分有效，首次不熄仍未修复）。

源码层判断：AOSP `Charger::UpdateScreenState` 在动画结束后调用 `healthd_draw_->blank_screen(true, drm_)`，随后**无条件**设置 `screen_blanked_=true`、停止下一次 screen transition，并写 `animation done`。本机二进制反汇编与该控制流对应。若 blank 调用没有真正把 DSI 面板关掉，程序不会检查/重试，于是第 0 帧文字和旧电量数字会留在屏幕上；按电源键重新开始动画后可在下一轮再尝试 blank。这解释现象，但“为何原子提交返回 0 而 DSI 仍 On”尚未定位。不可将 AOSP 源码称为本 ROM 实际源码；本 ROM 只有已编译的 charger 二进制。
