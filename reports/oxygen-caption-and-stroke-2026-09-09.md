# OxygenOS 全屏窗口菜单与质感轮廓光

目标：TB375FC / TB373FU 工程；本次实测 TB375FC、MT6897，ROM 标识 OPD2203_16.0.5.1000(EX01)。OPD2203 是移植来源标识。

## 全屏顶部三点：已恢复

当前 SystemUI 的 `FullscreenTaskWindowDecorController.forceCloseFullScreenWindowDecor()` 会检查 `Build.PRODUCT`。禁用名单包括 OPD2201、OPD2202、OPD2203、OPD2405、OPD2406、OPD2407、OPD2408。当前 ROM 的 `ro.product.name=OPD2203` 命中名单。

Launcher 自带的同名控制器没有这个额外检查，因此仅比较 Launcher 与 ColorOS 无法解释实际问题。平板 feature 与画面最小宽度在本机已满足。

`patch/build_fullscreen_caption.py` 保留原 SystemUI 所有文件，只修改 classes2.dex 中该名单初始化指令的一项：OPD2203 改为名单已有的 OPD2408，等效于移除 OPD2203，其他机型的判断保持不变。DEX 长度和布局不变，重新计算 SHA-1 与 Adler32。构建脚本验证原包哈希、指令唯一匹配、APK 条目变化范围和 ZIP CRC。

- 原 SystemUI SHA256：`72cfa6810c72d7aef8cfdfd8f57ee8f88117c2b5867f272d3700a08fe3c32dc7`
- 补丁 SystemUI SHA256：`1a80578af3928915e91dee9d78a90f8286754a38ef942e24d24e2f84e694e906`
- 模块 ID：`fixo_fullscreen_caption`
- 初始构建：`out/fullscreen-caption-trial-2026-09-09/`
- 用户确认与重启验证归档：`out/fullscreen-caption-confirmed-2026-09-09/`

独立模块只在启动完成后挂载补丁 APK，并重启一次 SystemUI。每次开机核对未覆盖的原 SystemUI 哈希；版本不一致则跳过。观察新进程 30 秒内是否持续存在，若不稳定则卸载挂载并标记停用。此观察不代表无限期防崩溃保证。

验证：用户明确回复“三个点已经恢复，我测试过了”；本机截图 `work/oxygen-ui-current-2026-09-09/caption-check.png` 显示顶部三点。模块安装后重启，日志 `caption-overlay=ok`，运行时 APK 哈希与补丁匹配，Settings 包仍正常注册。恢复模式/长期使用/其他 ROM 未测试。

原 Settings、相册、账号、显示及翻盖模块不包含此改动。禁用本模块并重启即可恢复原始 SystemUI。

## 质感轮廓光：尚未恢复

用户明确目标是 ColorOS 的质感轮廓光；已有视觉模糊、动画模糊不需要改动。当前 UXDesign 的界面和数据库均确认这两项已开启。ColorOS 基线见 `reports/coloros-ui-port-baseline-2026-09-09.md`。

实际 OxygenOS UXDesign 的 `assets/blurredTextureParam.json` 只有 BLURRED_VISION 和 ANIMATION_BLURRY，缺少 MATERIAL_STROKE；已有设置读写工具也不处理 `system_material_stroke_enable`。

本轮进一步反编译 ColorOS SystemUI，发现完整链路涉及：

- `QSPersonalityRepository`：监听 `system_material_stroke_enable`，提供分离与经典控制中心的轮廓状态。
- `NotificationEffectRepository`：通知效果中的轮廓状态。
- `LightStyleStrokeDrawable`、`QsSeekBarBlurManager`、`QsViewOutlineProvider`、`MixColorTileDrawable`：具体控件的轮廓参数和绘制。
- `CalculateGradientStrokeTools`：根据宽、高、圆角计算渐变线条参数。
- `BlurConfig` 与 `PlatformBlurDrawable`：传递轮廓参数到 posteffect 渲染端。

当前 OxygenOS 有较早版本的 `GradientStrokeLineParams`、`GradientStrokeCornerParams` 和 AGSL shader，但应用层 BlurConfig 没有 ColorOS 新增的 gradientStrokeLineParam / gradientStrokeCornerParam 接入。已核实接口差异：

| 调用 | 当前 OxygenOS | ColorOS 基线 |
| --- | --- | --- |
| setGradientStrokeLineParams | 返回 void | 返回 boolean |
| 角轮廓 | setGradientStrokeCornerParams(GradientStrokeCornerParams) | setCornerParams(CornerParams) |

因此只写数据库键或替换 UXDesign 不能恢复完整效果；直接搬新版本绘制类也存在确定的接口不匹配。底层旧版 shader 的存在说明可继续研究适配，不等于硬件不支持，也不等于已经移植成功。本轮未安装轮廓光测试包、未更改动画等级、未改轮廓数据库值，现有模糊效果保持原状。

后续可先在独立工作目录适配 ColorOS 的参数计算到旧版 posteffect 接口，验证单一通知/快捷面板控件的实际描边，然后接入设置开关和状态监听。需保留三点补丁；不要用完整 ColorOS SystemUI 覆盖已正常的 OxygenOS SystemUI。
