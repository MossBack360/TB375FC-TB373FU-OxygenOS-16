# OxygenOS 抬起亮屏定位与补丁

设备：TB375FC / MT6897
系统：OPD2203 OxygenOS 16 移植版

## 结论

问题由两层兼容差异叠加造成：

1. 关闭系统优化后，Settings 注入 AOSP Display 页面。AOSP `LiftToWakePreferenceController` 读写 `Settings.Secure.wake_gesture_enabled`，但当前 OPlus SettingsProvider 对这个键始终返回 0，因此开关立即关闭。
2. 改用 OPlus 原生键后，`ScreenOffGestureService` 能在熄屏时注册 MTK `TYPE_TILT_DETECTOR`。本机传感器实际报告标准事件值 `1.0`，OPD2203 的 OPlus 实现却只在 `0.0` 时调用 `OplusPowerManager.wakeUp()`，在 `1.0` 时延迟注销监听。

## 修复

- `fixo-settings-lift-to-wake-v3.7-magisk.zip`
  - 基于已确认稳定的 Settings 3.6，只重新构建并替换 `classes5.dex`。
  - 控制器改为读写 `oplus_customize_gesture_wake_up_arouse`。
  - 保留原签名 APK 参与开机扫描，启动完成后再 bind mount 修复载荷。
- `fixo-lift-to-wake-sensor-v1.0-magisk.zip`
  - 独立修补 OplusGestureUI，只替换 `classes.dex`。
  - `tilt=1.0` 进入原生唤醒分支，`tilt=0.0` 进入原取消分支。
  - 使用 MTK 硬件唤醒传感器；没有后台轮询、持续 partial wakelock 或加速度计耗电。

## 验证证据

- Settings 3.7 挂载 SHA-256：`d4ff666a9c9fec5c09ee3812b1d327f80600d438fafe36882cc271b17859c808`。
- OplusGestureUI 补丁挂载 SHA-256：`c146ba125a499aee2c9d70ef479d4ed45c111d011b7540ec242d88e58d500d43`。
- 数据库键能保持为 1，熄屏日志显示 `registerTiltSensor + sensorType = 22, sensor = tilt`。
- 补丁安装、开机挂载、服务启动均正常，用户已确认能够拿起亮屏。

## 已知触发限制

触发姿态带有明显的手机算法特征：平板横向普通拿起不稳定；将平板竖放，模拟手机从口袋中被拿出的动作时可以稳定触发。该限制来自参考 OPD2203 算法的姿态阈值与平板使用方式不匹配，记录为当前移植版特性，不再继续试验性修改。

## 系统优化开关

`Disable system optimization` 会改变 OPlus permission interception 状态。`DisplaySettingsFragment` 在拦截关闭时注入 AOSP `DisplaySettings`，所以会出现英文原生 Android 项目。已观察到 `Lift to wake`、`Tap to wake` 和 `Screen attention`；其他项目是否出现由各自 controller 的硬件与资源检测决定。
