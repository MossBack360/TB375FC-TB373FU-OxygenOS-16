# 已知问题记录

更新时间：2026-09-10

设备：小新 Pad Pro 2025（TB375FC，MT6897），移植 OxygenOS。

1. **相机来自 ZUI**
   - 主相机包为 `com.zui.camera`，另有 `com.zui.camera.assistant`、`com.zui.camera.qr`。
   - 当前没有 OxygenOS 的 `com.oplus.camera`；保留 ZUI 相机用于适配本机摄像头硬件。
2. **ZUI 相机中的“用户协议”和“隐私政策”：已修复**
   - 相机来自 ZUI，原系统缺少它跳转的 Lenovo 法务 Activity，因此点击时闪退或返回相机首页。
   - `fixo_zui_lenovo_privacy` v1.2 提供本机 ZUI 对应的 `ZuiLenovoPrivacy` 包，用户已确认入口可用。
3. **全屏应用顶部三点菜单：已修复，用户实测确认**
   - 2026-09-09 更正：`pull_click` 是最近任务卡片上的三点教学资源，不是全屏应用顶部三点。后者对应 WM Shell 的 `FullscreenTaskWindowDecorController` / `FullscreenCaptionHandleViewHolder`。
   - ColorOS 与参考 OPD2203 OxygenOS 的 Launcher 均包含该控制器，主要启用条件相同：平板识别、`debug.fullscreendecor.enable`、`ro.oplus.lightos`；单个任务还检查至少 600dp 的最小宽度及页面禁用名单等。
   - 自由浮窗教学页属于 `com.oplus.pscanvas`，两套参考配置均在 `disableFullScreenCaption` 中禁用此包，能解释进入该页时三点消失。不能据此推断所有 Settings 页面都被禁用。
   - 实际 OxygenOS SystemUI 的 `forceCloseFullScreenWindowDecor()` 额外检查机型禁用名单，其中包含 ROM 沿用的 `OPD2203`。此前只检查 Launcher 中的同名控制器，遗漏了 SystemUI 的独立限制。
   - 补丁只从 SystemUI 此名单排除 OPD2203，保留系统型号、窗口类型及页面禁用条件。用户已确认三点恢复；独立 Magisk 模块已安装并通过重启自动挂载检查。
   - 模块与证据见 `reports/oxygen-caption-and-stroke-2026-09-09.md`。不合并进 Settings 模块。
4. **OnePlus AI 功能不完整**
   - 已恢复国际版 AI 写作、AI 翻译、AI 语音摘要、AI 服务引擎等项目。
   - 其余项目受机型 feature、硬件 Provider 和产品策略控制。
   - 国内 `com.coloros.sceneservice` 会带来国际版没有的“个性化信息与服务”，不能作为国际版修复方案。
5. **Dolby 音效不可用**
   - 已恢复 ZUI DAP 库、配置、DaxService、全局效果及 Music Listener；设置界面和参数传递正常。
   - 实际播放仍无听觉变化，均衡器无效。音频流走 A2DP/deep-buffer，而 DAP 只挂在 primary output，诊断值为 `DAP Primary Mix: 0x0`。
   - v1.2、v1.3 与诊断结论已归档；继续修复需要处理 vendor 音频策略/DSP 路由，当前暂停。
6. **环境色自适应：已通过 MTK PQ bridge 修复**
   - 本机的 `tcs3701_cct` RGBW/CCT 传感器存在，但 OxygenOS 原生 AICCT 路径不能直接映射到 Lenovo/MTK 实现。
   - `fixo_display_pq` 将 OxygenOS 设置状态连接到本机 MTK PQ 引擎，用户已确认有效。
7. **屏幕色彩模式：已通过 MTK PQ bridge 修复，切换延迟较高**
   - OxygenOS 原来的请求无法直接驱动本机 SurfaceFlinger/vendor 映射。
   - `fixo_display_pq` 已恢复实际模式切换；肉眼生效延迟较长，用户接受为当前移植特性。

已归档并确认可用的 Settings、系统更新、翻盖模块不得被后续实验覆盖。

8. **抬起亮屏：已修复，保留手机取向的触发限制**
   - 关闭“系统优化”后出现的 AOSP `Lift to wake` 原本读写 `wake_gesture_enabled`；该键被当前 OPlus SettingsProvider 强制读成 0，所以开关会立即回弹。
   - Settings 3.7 已改为读写 OPlus 原生键 `oplus_customize_gesture_wake_up_arouse`，开关现在能够保持，OplusGestureUI 也会在熄屏时注册 MTK `tilt` 唤醒传感器。
   - 本机传感器实际只上报标准值 `1.0`，而 OPD2203 的 OplusGestureUI 把 `0.0` 当作唤醒、把 `1.0` 当作取消监听。独立模块 `fixo_lift_to_wake_sensor` 已交换这两个值的处理，不使用常驻加速度计轮询。
   - 模块已装入并由用户确认可以亮屏。由于 OPD2203 的算法按手机姿态设计，平板横向普通拿起时触发不稳定；将平板竖放并模拟“从口袋拿出手机”的动作可以稳定触发。
   - 该方向限制记录为当前移植版特性。若要进一步改善，需要调整或替换 vendor Sensor Hub 中的姿态阈值/识别算法，暂不继续修改。
9. **高端 OPD2514 参考包与移植实验**
   - 最初的 `OxygenOS OPD2514_16.0.8.301(EX01) A.30_IN.zip` 损坏；后续下载的 `ecb32008434b420c98515e3c41d5c4f1.zip` 可用于继续提取和对比。
   - 已尝试补充国际 AI 与质感轮廓光组件，但用户侧没有获得有效的新功能/渲染效果；相关模块已禁用，不能标记为已修复。
10. **“Disable system optimization”的实际影响**
   - 该开关会关闭 OPlus permission interception。Settings 检测到它关闭后，会在部分页面注入 AOSP 设置实现，因此出现英文原生项目，并非单纯改变性能调度。
   - 已确认可出现 AOSP Display 项目，例如 `Lift to wake`、`Tap to wake`，以及超时页面中的 `Screen attention`；具体项目仍受对应 controller 的硬件检测控制。
11. **微信扫一扫与 ZUI 相机启动异常：已修复**
   - 根因是 `/system_ext/etc/sys_camera_optimize_config.xml` 对微信/支付宝等扫描 Activity 启用不适配本机的 Oplus 相机启动优化，表现为延迟、回到微信地球页、概率性失败；分屏稳定是关键线索。
   - `fixo_camera_optimize_disable` v1.1 禁用该策略文件后，用户确认问题消失。不是 SELinux 或普通 Camera API 权限问题。
12. **SystemUI 窗口与返回手势：当前确认版本为 v0.5**
   - `fixo_fullscreen_caption` v0.5 同时保留顶部三点、底角拖动阶段的原始 v0.2 圆角修复，以及跟手返回手势。
   - 返回手势异常来自动画等级 3 时选择 `NonRubberBandBezierCalculator`；v0.5 只让此处使用 `RubberBandBezierCalculator`。
   - v0.4 曾尝试为正式浮窗交接增加 30↔50 px 圆角插值，用户认为视觉效果不好，已归档且不再使用。
13. **Oplus 动画等级**
   - 第三方 `TB375FC_ColosOS` 模块原本固定 `persist.sys.oplus.anim_level=3`；2026-09-09 的 OxygenOS 基线为 2。
   - 当前安装副本已改为 1，并在设备上保留原始 value-3 文件备份。设备时钟错误，不能用设备文件时间推断安装日期。
