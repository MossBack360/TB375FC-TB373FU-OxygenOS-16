# 底角动作与数字助理实验归档（已放弃）

日期：2026-09-12

## 结论

本实验不进入正式移植包，不再修改 Settings 或自由浮窗 APK。平板继续使用已确认的 `fixo_freeform_corner_gesture` v1.2 模块；要关闭底角自由浮窗，直接在 KernelSU/Magisk 中停用该模块并重启。

## 曾制作的原型

- 独立应用包名：`com.fixo.settings`
- 原显示名：`FixO 移植设置`（命名不采用）
- 原型包含“底角 Google / 自由浮窗 / 关闭”和“电源键 Google / 电源菜单”选项。
- 原型通过 `WRITE_SECURE_SETTINGS` 修改 SettingsProvider，并尝试用 root 守护脚本同步 panorama 属性。
- 原型存在运行期切换不稳定，因此停止维护，仅留作代码参考。
- 若未来恢复此界面，应使用更自然的中英文产品名，并至少提供 `values/strings.xml` 与 `values-zh-rCN/strings.xml`，不要把文字硬编码在布局或 smali 中。

## 已确认的相关键

- 手势导航底角 Google：`secure circle_to_search_corner_assist_enable_navi`
- 三键导航底角 Google：`secure circle_to_search_corner_assist_enable`
- 自由浮窗禁用状态：`secure panoramic_forced_disable_state`
- 自由浮窗总功能门：`persist.oplus.panorama.branch.enable`
- 长按电源键数字助理：`system quick_turn_on_voice_assistant`

自由浮窗 v1.2 在开机时将 panorama 属性设为 true，并将 `panoramic_forced_disable_state` 设为 0。因此最简单、稳定的开关方式是启用/停用整个模块，而不是额外维护热切换守护脚本。

## 未修复并记录的问题

“设置 > 辅助功能 > 自由浮窗”说明文字里的蓝色“Google 数字助理”链接仍指向 OPlus 原导航设置页面；移植环境中目标页没有对应选项，因此链接落点无效。按用户决定，不修改 `Settings.apk` 和 `OplusFlexibleWindowUI.apk`。

## 平板回退状态

- `com.fixo.settings` 已卸载。
- `secure fixo_corner_mode` 已删除。
- `secure circle_to_search_corner_assist_enable_navi=0`。
- `secure panoramic_forced_disable_state=0`。
- `persist.oplus.panorama.branch.enable=true`。
- v1.2 模块已重新安装到待更新目录，下一次重启恢复原 service 脚本。
- Settings APK SHA-256：`dd16f3af8b453a9f8ebe19ee9fcf22be80682a8f8aac528c81c379707e63e2c0`。
