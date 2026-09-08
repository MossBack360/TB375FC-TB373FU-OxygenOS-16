# 已知问题记录

更新时间：2026-09-08

设备：小新 Pad Pro 2025（TB375FC，MT6897），移植 OxygenOS。

1. **相机来自 ZUI**
   - 主相机包为 `com.zui.camera`，另有 `com.zui.camera.assistant`、`com.zui.camera.qr`。
   - 当前没有 OxygenOS 的 `com.oplus.camera`；保留 ZUI 相机用于适配本机摄像头硬件。
2. **设置中的“用户协议”和“隐私政策”点击后闪退**
   - 尚未修复，需要结合点击时 logcat、目标 Activity 和国际账号协议组件定位。
3. **“全屏应用”页面上方三点菜单缺失**
   - 当前判断由机型 feature 控制，需要匹配的机型 feature 或 Oplus framework 修改。
4. **OnePlus AI 功能不完整**
   - 已恢复国际版 AI 写作、AI 翻译、AI 语音摘要、AI 服务引擎等项目。
   - 其余项目受机型 feature、硬件 Provider 和产品策略控制。
   - 国内 `com.coloros.sceneservice` 会带来国际版没有的“个性化信息与服务”，不能作为国际版修复方案。
5. **Dolby 音效不可用**
   - Dolby 上层请求的 effect UUID 在当前 vendor 中没有注册，也缺对应 soundfx 实现与 `com.dolby.daxservice`。
   - 需要刷回官方 ZUI 后采集同芯片的完整音效实现再判断移植范围。
6. **环境色自适应无实际效果**
   - 本机有 `tcs3701_cct` RGBW/CCT 传感器，开关和数据库正常。
   - 开启时 AICCT framework 报 `sensor or listener is null`，需要对照 ZUI 的传感器映射和 framework 配置。
7. **屏幕色彩模式肉眼无变化**
   - 选项会更新数据库并调用 ColorDisplayService。
   - SurfaceFlinger 不认识当前请求的映射并回退默认色彩模式，需要对照 ZUI vendor 的色彩配置与校准。

已归档并确认可用的 Settings、系统更新、翻盖模块不得被后续实验覆盖。
