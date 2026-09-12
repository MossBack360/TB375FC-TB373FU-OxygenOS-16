# TB375FC 拿起设备唤醒胶水模块

OxygenOS 的设置界面使用 `ambient_tilt_to_wake` 和 MTK `tilt`（类型 22）；ZUI 则使用硬件提供的标准 `wake_gesture`（类型 23），后者在本机上更敏感。

本模块不替换 SettingsProvider、services.jar 或 SystemUI。开机完成后，它以一个很小的 `app_process` 进程注册类型 23 的一次性唤醒传感器；收到事件后调用系统 PowerManager 唤醒屏幕，并重新注册下一次事件。后台脚本每 3 秒跟随“拿起设备唤醒”开关的 `ambient_tilt_to_wake` 值启停进程。

禁用模块并重启即可完整撤销。运行日志位于模块目录的 `runtime.log`。
