# ColorOS 质感视效与全屏窗口菜单：移植前基线

采集日期：2026-09-09。目标硬件 TB375FC（MT6897）。当前 ColorOS 移植来源标识 OPD2601，构建 OPD2601_16.0.7.201(CN01)。OPD2203 是 OxygenOS 参考机型，不是本工程目标硬件。

## 状态与归档

本轮只提取、反编译和读取运行状态，没有安装模块、修改属性或数据库。现阶段还没有可确认有效的新移植补丁。

本地目录：`work/coloros-opd2601-baseline-2026-09-09/`。原始文件保持独立，未覆盖以前的模块归档。

- APK：Settings、SystemUI、OplusLauncher、Wallpapers、UXDesign、OplusFlexibleWindowUI、OplusExSystemService。
- framework：framework.jar、services.jar、oplus-framework.jar、oplus-services.jar、framework-res.apk、oplus-framework-res.apk。
- configs：窗口缩放策略、分屏/浮窗应用配置、my_stock/my_product 的 Oplus feature 与 app-feature 文件、部分产品 permissions 配置。
- 运行记录：runtime-ui-properties.txt、runtime-ui-settings.txt、window-baseline.txt、systemui-service.txt；部分页面截图。
- SHA256 清单：SHA256SUMS.txt，包含原始 APK、JAR、XML 和上述运行记录，不包含反编译生成目录。

当前 shell 找不到 su；OplusFrameworkResTabletOverlay.apk 的 pull 被设备拒绝。因此此目录是针对本轮问题的基线，不是完整 ROM/设备备份。该 overlay 的当前版本尚未提取；参考国际版原包有副本。当前已取文件足以开始下一轮 OxygenOS 对照。

## 质感视效

页面路径实测：Settings → Wallpapers 的 PersonalActivity / PersonalMoreActivity → `com.oplus.uxdesign/.blurSettings.BlurredTextureActivity`。

Action：`com.oplus.uxdesign.action.JUMP_TO_BLURRED_TEXTURE`。界面控制在 UXDesign；入口在 Wallpapers，效果还依赖 Launcher、SystemUI 与图形框架。

| 项目 | 当前 ColorOS UXDesign 16.1.0 | OPD2203 OxygenOS UXDesign 16.0.7 |
| --- | --- | --- |
| 视觉模糊 | 有 | 有 |
| 动画模糊 | 有 | 有 |
| 质感轮廓光 | 有 MATERIAL_STROKE 配置及读写代码 | 本次参考 APK 未包含对应配置/页面功能 |

直接证据是两包的 `assets/blurredTextureParam.json`、BlurredTextureActivity 与设置读写工具类。ColorOS 的 `c7/a.smali`，OxygenOS 的 `a7/a.smali`。

Settings.System 键及当前值：

- `system_material_blur_enable=1`
- `animationBlurrySwitch=1`
- `system_material_stroke_enable=1`（ColorOS 新项）
- `system_material_blur_changed_by_user=1`

OxygenOS Wallpapers 的 MoreNewPersonalViewModel 在动画等级大于 2 时跳过 `page_blurred_texture_key`。其 `com.oplus.wallpapers.rely.utils.w.b()` 优先读取 `persist.sys.oplus.anim_level`，未设置时才查询 OplusPlatformLevelUtils。

当前 ColorOS 的该属性为 1；参考 OxygenOS 的 my_product/build.prop 也为 1。因此代码确实有分级条件，但尚不能认定这就是实际移植包入口缺失的根因。

下一轮优先验证实际 OxygenOS 的包版本、属性、页面是否可启动、开关是否改变系统效果。若仅入口/分级异常，修复已有国际版组件；轮廓光需要额外确认渲染端支持，不能仅加菜单或写一个数据库键就宣称成功。两套组件代际不同，不直接整包覆盖 SystemUI/framework。

## 全屏应用顶部三点与底角浮窗手势

`pull_click` 对应最近任务卡片右上角三点，旧记录已更正。用户所说的全屏顶部菜单在 WM Shell 中对应：

- `com.android.wm.shell.windowdecor.FullscreenTaskWindowDecorController`
- `com.android.wm.shell.windowdecor.viewholder.FullscreenCaptionHandleViewHolder`
- `com.android.wm.shell.fullscreen.FullscreenCaptionHandleMenu`

当前 ColorOS SystemUI 和 Launcher 的 DEX 都含这些类；Launcher 已反编译定位。参考 OxygenOS Launcher 也有该控制器，`<clinit>`、`fullscreenWindowDecorEnabled`、`isLargeEnough` 的已检查逻辑相同。不能把 FlexibleTaskIndicator 当成全屏三点的同义词。

已确认的控制条件：

- `ro.oplus.lightos` 为 true 时总入口关闭；默认 false。
- `debug.fullscreendecor.enable` 控制总入口，默认 true；当前 ColorOS 未设置该属性，故空值不代表关闭。
- 平板判断依赖 `oplus.hardware.type.tablet` 的 OplusFeatureConfigManager 查询；只有 ro.build.characteristics=tablet 不足以证明此查询结果。
- 任务需要符合窗口模式、主屏幕、普通 Activity 类型、最小宽度至少 600dp 等要求。ColorOS 本轮显示配置 sw775dp。
- 超级省电、儿童模式、禅定模式、特定场景与包/Activity 禁用名单也会影响显示。

当前 ColorOS `sys_wms_split_app_ps.xml` 含：

```xml
<disableFullScreenCaption attr="com.oplus.pscanvas"/>
```

参考 OxygenOS 也有这条。自由浮窗教学页正属于此包，控制器会调用 `SplitScreenAppConfig.inDisableFullscreenCaptionList(topActivity)`；这与用户观察到进入教学页后三点消失一致。该观察不能用于认定 Settings 所有页面都不可浮窗，也不能解释 OxygenOS 所有应用都缺三点。

底角手势的教学字符串是 FlexibleWindowUI 中的 `freeform_scale_open` / `freeform_scale_open_summary`，包括 pad 动画。动画本身不实现手势；仍需 WM Shell、系统窗口管理与 FlexibleWindow 配合。两项属于相关的多窗口功能，但不等于同一个开关。

## 切回 OxygenOS 后的检查顺序

1. 确认刷机结束、ADB 已可用，再采集实际版本、UXDesign/Wallpapers/Launcher/SystemUI/PSCanvas 路径及哈希。当前本地国际包只是参考，不能代替实际安装状态。
2. 比较 anim_level、lightos、fullscreendecor 属性；核对 Oplus 平板 feature 的实际加载情况、密度/最小宽度和运行时窗口策略。
3. 检查质感页面跳转，按开关观察通知中心、文件夹和启动退出动画。轮廓光单独确认。
4. 对同一个普通全屏应用、Settings 主页和 PSCanvas 教学页观察菜单；检查系统日志中的 FullscreenTaskHandleController / FullscreenWindowDecoration，再测试底角拖拽。
5. 定位后先做最小可回滚模块。只恢复缺失入口/配置时，保留国际版原组件；确实缺代码时再评估组件移植。

本轮未保证这两项已能移植成功，未要求更换目标机型标识。需要下一轮实际 OxygenOS 数据才能判断是移植改动、组件版本差异还是机型策略。

## 网上资料的适用范围

[OnePlus 官方 OxygenOS 16 页面](https://www.oneplus.com/ca_en/oxygenos16) 对部分多窗口能力明确列出机型限制，说明同一大版本存在机型差异；该说明不是 OPD2203 顶部三点缺失的直接证据。[OPPO 官方自由浮窗教学](https://www.oppo.com/cn/how-to/list/video-31/) 可用于确认功能名称。具体移植判断以上述本地代码及实际设备对照为准。
