# 声道随屏幕旋转桥接 v2.1

当前 OxygenOS 已将屏幕旋转发送给 AudioFlinger，但 MT6897/Awinic 音频 HAL
实际还接受厂商参数 `gsensor_rotation`。本模块监听显示旋转，并在角度变化时调用
系统自带的 `/system_ext/bin/AudioSetParam` 发送：

- `mRotation=0` -> `gsensor_rotation=270`
- `mRotation=1` -> `gsensor_rotation=0`
- `mRotation=2` -> `gsensor_rotation=90`
- `mRotation=3` -> `gsensor_rotation=180`

这是联想 ZUI 使用的坐标转换。HAL 只会对发送参数时已经打开的扬声器输出流
执行换向，因此脚本每两秒重发一次当前角度，新开始的播放也能在两秒内应用。

模块不替换 `services.jar`。运行记录位于：
`/data/local/tmp/fixo_speaker_rotation.log`。
