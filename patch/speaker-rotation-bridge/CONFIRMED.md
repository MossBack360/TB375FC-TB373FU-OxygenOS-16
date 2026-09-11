# TB375FC/TB373FU 扬声器声道随屏幕旋转

状态：2026-09-11 OxygenOS 16 实机确认成功。

刷入文件：`fixo-speaker-rotation-bridge-v2.1-magisk.zip`

SHA-256：`9C40CB9575498511E3E8E4FD206232802F3BCE6E36B2EE29005F5717EF0FD92E`

## 实现

- 保留 Android 原生 `ro.audio.monitorRotation=true`。
- 后台读取 `mRotation`，通过系统自带 `AudioSetParam` 向 MT6897/Awinic
  音频 HAL 发送 `gsensor_rotation`。
- 使用联想 ZUI 坐标转换：`0→270`、`90→0`、`180→90`、`270→180`。
- 每两秒重发当前角度，使新打开的扬声器音频流也能应用声道方向。
- 不替换 `services.jar`，不影响有线、USB 或蓝牙耳机输出。

模块 ID：`fixo_speaker_rotation_prop`，版本：`2.1`。

旧的 `speaker_rotation_fix` 会覆盖不兼容的 `services.jar` 并导致卡二屏，禁止使用。
